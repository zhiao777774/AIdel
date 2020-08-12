import sys
import signal
import time
import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera

from .file_controller import ROOT_PATH
# from .image_processor import ImageProcessor
from .speech_service import SpeechService, Responser
from .detector import detect, BoundingBox
from .obstacle_dodge_service import Dodger, Maze, generate_maze, PathNotFoundError
from .distance_measurementor import Calibrationor, Measurementor
from .environmental_model import create_environmental_model, disconnect_environmental_model_socket
from .guardianship_service import GuardianshipService
from .sensor_module import HCSR04, GPS, MPU6050, destroy_sensors


_CALIBRATION_DISTANCE = 35
_FOCALLEN = 14.536741214057509
_FRAME_SIZE = (960, 720)
_FRAME_RATE = 50
_RESOLUTION = 120

def initialize():
    camera = PiCamera()
    camera.resolution = _FRAME_SIZE
    camera.framerate = _FRAME_RATE
    raw_capture = PiRGBArray(camera)
    # out = cv2.VideoWriter('', 
    #     cv2.VideoWriter_fourcc(*'XVID'), _FRAME_RATE, _FRAME_SIZE)

    time.sleep(0.1)
    '''
    def _image_preprocess(frame):
        processor = ImageProcessor(frame)
        processor.basic_preprocess()
        return processor.frame

    def _project_to_2d(frame):
        processor = ImageProcessor(frame)
        return processor.cvt_to_overlook(frame)
    '''
    _signal_handle()
    _init_services()
    _enable_sensors()
    _DICT_SERVICE['GuardianshipService'].mpu = _DICT_SENSORS['MPU6050']
    
    dodger = Dodger()
    resp = Responser()

    for frame in camera.capture_continuous(raw_capture, format='bgr', use_video_port=True):
        frame = frame.array
        result, dets = detect(frame)

        bboxes = []
        if dets:
            bboxes = _calc_distance(result, dets)
            bboxes = _calc_angle(result, bboxes)
            create_environmental_model(
                file_path = f'{ROOT_PATH}/data/environmentalModel.json',
                height = result.shape[0], width = result.shape[1],
                resolution = _RESOLUTION, bboxes = bboxes)

        cv2.namedWindow('result', cv2.WINDOW_NORMAL)
        cv2.imshow('result', result)
        # out.write(result)
        # _save_image(result)
        
        if bboxes:
            h = int(result.shape[0] / 2)
            w = result.shape[1]
            maze = generate_maze(data = bboxes, height = h, width = w,
                benchmark = h, resolution = _RESOLUTION)
            maze = Maze(maze)

            try:
                dirs = dodger.solve(maze)
            except (PathNotFoundError, IndexError) as err:
                cv2.waitKey(1) & 0xFF
                raw_capture.truncate(0)
                print(err)
                continue     

            print(maze)
            print(dirs)
            res_audio_file = resp.decide_response(dirs[0])
            resp.play_audio(res_audio_file)
        
        cv2.waitKey(1) & 0xFF
        raw_capture.truncate(0)


_DICT_SERVICE = {}
def _init_services():
    serivces = [
        SpeechService(),
        # GuardianshipService(interval=6)
    ]

    for service in serivces:
        service.setDaemon(True)
        service.start()
        _DICT_SERVICE[type(service).__name__] = service

_DICT_SENSORS = {}
def _enable_sensors():
    sensors = [
        HCSR04(trigger_pin=23, echo_pin=24),
        # GPS(port='/dev/ttyAMA0'),
        MPU6050()
    ]

    for sensor in sensors:
        sensor.setDaemon(True)
        sensor.start()
        _DICT_SENSORS[type(sensor).__name__] = sensor

def _generate_bboxes(dets):
    return [BoundingBox(det) for det in dets]

def _calc_distance(frame, dets):
    h = frame.shape[0]
    w = frame.shape[1]

    bboxes = _generate_bboxes(dets)
    bboxes = [bbox for bbox in bboxes
              if bbox.coordinates.lb.y >= int(h / 2)]
    bboxes = [bbox for bbox in bboxes
              if bbox.width * bbox.height >= int((h / 4) * (w / 4))]

    for bbox in bboxes:
        distance = _measure_distance(_CALIBRATION_DISTANCE, _FOCALLEN, bbox)
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
    print(f"min enclosing circle's radius: {size}")

    measurementor = Measurementor(focallen)
    distance = measurementor.measure(size, rad)

    if distance < calibration_distance:
        distance = calibration_distance + distance
    print(f'Distance in cm {distance}')

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
        
        print(f'angle degrees {angle}')
        x = int(v2_x - bbox.width / 4)
        y = int(bbox.coordinates.lt.y - 25)
        cv2.putText(frame, text=f'{angle}°', org=(x, y),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.50, 
                    color=(0, 0, 255), thickness=2)
    
    return bboxes

def _save_image(image):
    lat, lng = _DICT_SENSORS['GPS'].latlng()

    _DICT_SERVICE['GuardianshipService'].data = {
        'image': image,
        'lat': lat,
        'lng': lng
    }

def _signal_handle():
    def _handler(signal, frame):
        cv2.destroyAllWindows()
        destroy_sensors()
        _DICT_SERVICE['GuardianshipService'].stop()
        disconnect_environmental_model_socket()
        sys.exit(0)

    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)