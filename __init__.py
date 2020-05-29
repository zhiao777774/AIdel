from timeit import default_timer as timer
import sys, signal
import cv2

from .image_processor import ImageProcessor
from .detector import detect, BoundingBox
from .obstacle_dodge_service import Dodger

def initialize():
    capture = cv2.VideoCapture(0) #0代表從攝像頭開啟
    '''
    frame_size = (640, 360)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_size[0])
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_size[1])
    video_FourCC = cv2.VideoWriter_fourcc(*'XVID')
    video_fps = 100.0
    video_size = frame_size
    out = cv2.VideoWriter('', video_FourCC, video_fps, video_size)
    '''
    if not capture.isOpened():
        capture.open()
    
    def _image_preprocess(frame):
        processor = ImageProcessor(frame)
        processor.basic_preprocess()
        return processor.frame

    def _project_to_2d(frame):
        processor = ImageProcessor(frame)
        return processor.cvt_to_overlook(frame)
    
    accum_time = 0
    curr_fps = 0
    fps = "FPS: ??"
    prev_time = timer()

    _signal_handle()
    #_init_services()
    while True:
        frame = capture.read()[1]
        #frame = _image_preprocess(frame)
        #frame = _project_to_2d(frame)
        result = detect(frame)
                
        curr_time = timer()
        exec_time = curr_time - prev_time
        prev_time = curr_time
        accum_time = accum_time + exec_time
        curr_fps = curr_fps + 1
        if accum_time > 1:
            accum_time = accum_time - 1
            fps = "FPS: " + str(curr_fps)
            curr_fps = 0

        cv2.putText(result, text = fps, org = (3, 15), fontFace = cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale = 0.50, color = (255, 0, 0), thickness = 2)
        cv2.namedWindow("result", cv2.WINDOW_NORMAL)
        cv2.imshow("result", result)
        #out.write(result)
        #bboxes = _generate_bboxes(dets)


from .speech_service import SpeechService
        
_DICT_SERVICE = {}
def _init_services():
    global _DICT_SERVICE

    serivces = [
        SpeechService()
    ]

    for service in serivces:
        service.setDaemon(True)
        service.start()
        _DICT_SERVICE[type(service).__name__] = service

def _generate_bboxes(dets):
    return [BoundingBox(det) for det in dets]

def _signal_handle():
    _handler = lambda signal, frame: sys.exit(0)

    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)