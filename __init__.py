import sys
import shutil
import signal
import time
import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera

import utils
from .file_controller import ROOT_PATH, AUDIO_PATH
from .image_processor import NPImage
from .speech_service import SpeechService, Responser
from .detector import detect, BoundingBox
from .obstacle_dodge_service import Dodger, Maze, generate_maze, PathNotFoundError
from .distance_measurementor import Calibrationor, Measurementor
from .environmental_model import create_environmental_model, disconnect_environmental_model_socket
from .guardianship_service import GuardianshipService
from .sensor_module import HCSR04, GPS, MPU6050, Buzzer, Frequency, EmergencyButton, destroy_sensors
# from .beacon_scanner import BeaconScanner


_CALIBRATION_DISTANCE = 35
_FOCALLEN = 14.536741214057509
_FRAME_SIZE = (960, 720)
_FRAME_RATE = 50
_VIDEO_RATE = 20
_RESOLUTION = 60
utils.initialize_vars()

def initialize():
    camera = PiCamera()
    camera.resolution = _FRAME_SIZE
    camera.framerate = _FRAME_RATE
    raw_capture = PiRGBArray(camera)
    # out = cv2.VideoWriter(
    #     f'output_{time.strftime("%Y%m%d-%H%M", time.localtime())}.mp4', 
    #     cv2.VideoWriter_fourcc(*'XVID'), _VIDEO_RATE, _FRAME_SIZE)
    time.sleep(0.1)

    def _truncate_frame():
        cv2.waitKey(1) & 0xFF
        raw_capture.truncate(0)

    _signal_handle()
    _init_services()
    _enable_sensors()
    # _DICT_SERVICE['GuardianshipService'].mpu = _DICT_SENSORS['MPU6050']
    # _DICT_SERVICE['GuardianshipService'].buzzer = _DICT_SENSORS['Buzzer']
    
    dodger = Dodger()
    resp = Responser()
    
    for frame in camera.capture_continuous(raw_capture, format='bgr', use_video_port=True):
        frame = frame.array
        result, dets = detect(frame)

        h = result.shape[0]
        w = result.shape[1]

        bboxes = []
        bboxes += _find_contours(result, threshold = int((h / 4) * (w / 4)))
        if dets or bboxes:
            bboxes = _calc_distance(result, dets, bboxes)
            bboxes = _calc_angle(result, bboxes)
            '''
            create_environmental_model(
                file_path = f'{ROOT_PATH}/data/environmentalModel.json',
                image = result, resolution = _RESOLUTION, bboxes = bboxes)
            '''

        cv2.namedWindow('result', cv2.WINDOW_NORMAL)
        cv2.imshow('result', result)
        # out.write(result)

        utils.GLOBAL_IMAGE = frame
        utils.GLOBAL_DATASET = bboxes
        # utils.GLOBAL_LATLNG.latitude = _DICT_SENSORS['GPS'].latitude
        # utils.GLOBAL_LATLNG.longitude = _DICT_SENSORS['GPS'].longitude
        hcsr04_distance = _DICT_SENSORS['HCSR04'].distance

        if hcsr04_distance and float(hcsr04_distance) < 50:
            res_audio_file = resp.decide_response(f'stop,{float(hcsr04_distance)}')
            resp.play_audio(res_audio_file)
            _DICT_SENSORS['Buzzer'].buzz(Frequency.ALERT, 0.2, 1)
            
            _truncate_frame()
            continue  
        
        if bboxes:
            h = int(result.shape[0] / 2)
            maze = generate_maze(data = bboxes, height = h, width = w,
                benchmark = h, resolution = _RESOLUTION)
            maze = Maze(maze)

            try:
                dirs = dodger.solve(maze)
            except (PathNotFoundError, IndexError) as err:
                _truncate_frame()
                print(err)
                continue     

            print(maze)
            print(dirs)
            res_audio_file = resp.decide_response(f'{dirs[0]},{bboxes[0].distance}')
            resp.play_audio(res_audio_file)

            if dirs[0] in ('v', 'stop'):
                _DICT_SENSORS['Buzzer'].buzz(Frequency.ALERT, 0.2, 1)
        
        _truncate_frame()


_DICT_SERVICE = {}
def _init_services():
    serivces = [
        SpeechService(),
        # GuardianshipService(interval=6),
        # BeaconScanner()
    ]

    for service in serivces:
        service.setDaemon(True)
        service.start()

        service_name = type(service).__name__
        _DICT_SERVICE[service_name] = service
        utils.GLOBAL_LOGGER.info(f'{service_name} is started.')

_DICT_SENSORS = {}
def _enable_sensors():
    sensors = [
        HCSR04(trigger_pin=23, echo_pin=24),
        # GPS(port='/dev/ttyAMA0'),
        MPU6050(),
        # EmergencyButton(button_pin=26, 
        #   service=_DICT_SERVICE['GuardianshipService'])
    ]

    for sensor in sensors:
        sensor.setDaemon(True)
        sensor.start()

        sensor_name = type(sensor).__name__
        _DICT_SENSORS[sensor_name] = sensor
        utils.GLOBAL_LOGGER.info(f'{sensor_name} is enabled.')

    _DICT_SENSORS['Buzzer'] = Buzzer(buzzer_pin=16)
    utils.GLOBAL_LOGGER.info(f'{type(_DICT_SENSORS["Buzzer"]).__name__} is enabled.')

def _generate_bboxes(dets):
    return [BoundingBox(det) for det in dets]

def _calc_distance(frame, dets, bboxes):
    h = frame.shape[0]
    w = frame.shape[1]

    bboxes += _generate_bboxes(dets)
    bboxes = [bbox for bbox in bboxes
              if bbox.coordinates.lb.y >= int(h / 2)]
    bboxes = [bbox for bbox in bboxes
              if bbox.width * bbox.height >= int((h / 4) * (w / 4))]

    for bbox in bboxes:
        distance = _measure_distance(_CALIBRATION_DISTANCE, _FOCALLEN, bbox)
        distance = 1.2687 * distance + 4.5514 # 利用迴歸線校正距離
        distance = round(distance, 2)
        bbox.distance = distance
        x = int(bbox.center()[0] - bbox.width / 4)
        y = int(bbox.coordinates.lt.y - 10)
        cv2.putText(frame, text=f'{distance}cm', org=(x, y),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.50, 
                    color=(0, 0, 255), thickness=2)

    return bboxes

def _measure_distance(calibration_distance, focallen, bbox):
    rad = bbox.width
    size = bbox.minEnclosingCircle()

    measurementor = Measurementor(focallen)
    distance = measurementor.measure(size, rad)

    if distance < calibration_distance:
        distance = calibration_distance + distance

    return distance

def _calc_angle(frame, bboxes):
    h = frame.shape[0]
    w = frame.shape[1]

    for bbox in bboxes:
        v2_x, v2_y = bbox.center()
        v1 = np.array([w / 2, h])
        v2 = np.array([v2_x, v2_y])
        line_v1 = np.sqrt(v1.dot(v1))
        line_v2 = np.sqrt(v2.dot(v2))

        cos_angle = v1.dot(v2) / (line_v1 * line_v2)
        angle = np.arccos(cos_angle)
        angle = round(angle * 360 / 2 / np.pi, 1)
        bbox.angle = angle
        
        x = int(v2_x - bbox.width / 4)
        y = int(bbox.coordinates.lt.y - 25)
        cv2.putText(frame, text=f'{angle}°', org=(x, y),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.50, 
                    color=(0, 0, 255), thickness=2)
    
    return bboxes

def _find_contours(frame, threshold = 30):
    dets = []

    for cnt in NPImage(frame).find_contours():
        area = cv2.contourArea(cnt)
        if area >= threshold:
            x, y, w, h = cv2.boundingRect(cnt)
            dets.append(('unknown', 1, (x, y, x + w, y + h)))
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return _generate_bboxes(dets)

def _signal_handle():
    def _handler(signal, frame):
        cv2.destroyAllWindows()
        destroy_sensors()
        # _DICT_SERVICE['GuardianshipService'].stop()
        disconnect_environmental_model_socket()
        shutil.rmtree(f'{AUDIO_PATH}/temp', ignore_errors = True)
        sys.exit(0)

    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)