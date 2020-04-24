import sys, signal
import cv2
import numpy as np

from .image_processor import ImageProcessor
from .detector import detect, BoundingBox
from .obstacle_dodge_service import Dodger

def initialize():
    capture = cv2.VideoCapture(0) #0代表從攝像頭開啟
    
    if not capture.isOpened():
        capture.open()
    
    def _image_preprocess(frame):
        processor = ImageProcessor(frame)
        processor.basic_preprocess()
        return processor.frame

    def _project_to_2d(frame):
        processor = ImageProcessor(frame)
        processor.canny()
        processor.region_of_interest()
        processor.hough_lines()
        processor.optimize_lines(frame)
        return processor.cvt_to_overlook(frame)
    
    _signal_handle()
    _init_services()
    while True:
        frame = capture.read()[1]
        frame = _image_preprocess(frame)
        #frame = _project_to_2d(frame)
        #h, w, _ = frame.shape
        
        """
        dets = detect(frame)
        bboxes = _generate_bboxes(dets)
        dop_vals = list(Dodger.calc(bbox) for bbox in bboxes)
        dop_tree = Dodger.get_DOP(dop_vals)
        """  
        

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