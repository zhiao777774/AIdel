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
from .environmental_model import create_environmental_model


_CALIBRATION_DISTANCE = 35
_FOCALLEN = 14.536741214057509
_FRAME_SIZE = (630, 360)
_FRAME_RATE = 50

def initialize():
    camera = PiCamera()
    camera.resolution = _FRAME_SIZE
    camera.framerate = _FRAME_RATE
    rawCap = PiRGBArray(camera)

    time.sleep(0.1)
    '''
    video_fps = 60.0
    out = cv2.VideoWriter('', cv2.VideoWriter_fourcc(*'XVID'), video_fps, _FRAME_SIZE)
    '''
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
    # _init_services()
    dodger = Dodger()
    resp = Responser()

    for frame in camera.capture_continuous(rawCap, format='bgr', use_video_port=True):
        frame = frame.array
        result, dets = detect(frame)

        bboxes = []
        if dets:
            bboxes = _calc_distance(result, dets)
            create_environmental_model('data/environmentalModel.json', bboxes)

        cv2.namedWindow('result', cv2.WINDOW_NORMAL)
        cv2.imshow('result', result)
        # out.write(result)
        '''
        if bboxes:
            h = int(result.shape[0] / 2)
            w = result.shape[1]
            maze = generate_maze(data = bboxes, height = h, width = w,
                benchmark = h, resolution = 90)
            maze = Maze(maze)

            try:
                dirs = dodger.solve(maze)
            except PathNotFoundError as err:
                print(err)
                continue
            except IndexError:
                continue

            res_text = resp.decide_response(dirs[0])
            #resp.tts(res_text)
            #resp.play_audio(res_text)
        '''
        cv2.waitKey(1) & 0xFF
        rawCap.truncate(0)


_DICT_SERVICE = {}
def _init_services():
    serivces = [
        SpeechService()
    ]

    for service in serivces:
        service.setDaemon(True)
        service.start()
        _DICT_SERVICE[type(service).__name__] = service

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

def _signal_handle():
    def _handler(signal, frame):
        cv2.destroyAllWindows()
        sys.exit(0)

    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)