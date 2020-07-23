import sys
import signal
import time
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera

#from .image_processor import ImageProcessor
from .speech_service import SpeechService, Responser
from .detector import detect, BoundingBox
from .obstacle_dodge_service import Dodger, Maze, generate_maze, PathNotFoundError
from .distance_measurementor import Calibrationor, Measurementor
from .environmental_model import create_environmental_model, disconnect_environmental_model_socket
from .db_handler import MongoDB, np_cvt_base64img
from .sensor_module import HCSR04, LSM6DS3, destroy_sensors


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
    with MongoDB('120.125.83.10', '8080') as db:
        dodger = Dodger()
        resp = Responser()

        for frame in camera.capture_continuous(raw_capture, format='bgr', use_video_port=True):
            frame = frame.array
            result, dets = detect(frame)

            bboxes = []
            if dets:
                bboxes = _calc_distance(result, dets)
                create_environmental_model(
                    file_path = 'data/environmentalModel.json',
                    height = result.shape[0], width = result.shape[1],
                    resolution = _RESOLUTION, bboxes = bboxes)

            cv2.namedWindow('result', cv2.WINDOW_NORMAL)
            cv2.imshow('result', result)
            # out.write(result)
            
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
        SpeechService()
    ]

    for service in serivces:
        service.setDaemon(True)
        service.start()
        _DICT_SERVICE[type(service).__name__] = service

_DICT_SENSORS = {}
def _enable_sensors():
    sensors = [
        HCSR04(trigger_pin=16, echo_pin=18),
        #LSM6DS3()
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
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.50, color=(0, 0, 255), thickness=2)

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
'''
def _save_image(image, db, is_first = False):
    t = time.localtime()

    n = 0
    while t.tm_min > 6 * n: n += 1

    diff_min = 6 * n - t.tm_min
    diff_sec = 60 - t.tm_sec
    diff_time = diff_min * 60 + diff_sec

    if is_first or diff_min <= 0: _save(image, db)

    @set_interval(diff_time, 1)
    def _save(image, db):
        t = time.localtime()
        fdate = time.strftime('%Y/%m/%d', t)
        ftime = f'{t.tm_hour}:{"00" if t.tm_min < 30 else "30"}'
        lat = 0
        lng = 0
        address = ''

        insert_data = {
            'date': fdate,
            'data': [{
                'time': ftime,
                'data': [{
                    'id': t.tm_min / 6,
                    'image': np_cvt_base64img(image),
                    'description': address
                }]
            }],
            'locations': [{
                'latitude': lat,
                'longitude': lng
            }]
        }

        def _insert(data):
            insert_data['data'] += data['data']
            insert_data['locations'] += data['locations']
            db.insert({
                'collection': 'historicalImage',
                'data': insert_data
            })

        db.select({
            'collection': 'historicalImage',
            'filter': { 'date': fdate }
        }, _insert)
'''
def _signal_handle():
    def _handler(signal, frame):
        cv2.destroyAllWindows()
        destroy_sensors()
        disconnect_environmental_model_socket()
        sys.exit(0)

    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)