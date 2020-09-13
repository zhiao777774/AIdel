import time
import logging
from threading import Thread
from dataclasses import dataclass


class Logger:
    def __init__(self):
        logging.basicConfig(
            format = '%(asctime)s : %(levelname)s : %(message)s', 
            level = logging.INFO)
    
    def info(self, message):
        logging.info(message)

    def warning(self, message):
        logging.warning(message)

    def error(self, message):
        logging.error(message)

    def critical(self, message):
        logging.critical(message)


class Timer:
    def __init__(self):
        self._start_time = None
        self._elapsed_time = 0
        self._is_stop = False

    def start(self):
        if self._start_time: return

        self._is_stop = False
        self._elapsed_time = 0
        self._start_time = time.perf_counter()
        while not self._is_stop:
            end_time = time.perf_counter()
            self._elapsed_time += end_time - self._start_time
            self._start_time = time.perf_counter()
            time.sleep(0.01)

    def stop(self):
        self._is_stop = True
        self._start_time = None
            
    @property
    def elapsed_time(self):
        return round(self._elapsed_time, 2)


class AsyncTimer(Thread, Timer):
    def __init__(self):
        Thread.__init__(self)
        Timer.__init__(self)

    def start(self):
        Thread.setDaemon(self, True)
        Thread.start(self)

    def run(self):
        Timer.start(self)


@dataclass
class LatLng:
    latitude: float = 0.0
    longitude: float = 0.0


def initialize_vars():
    global GLOBAL_LOGGER
    GLOBAL_LOGGER = Logger()
    
    global GLOBAL_SPEECH_CONTENT
    GLOBAL_SPEECH_CONTENT = ''

    global GLOBAL_IMAGE
    GLOBAL_IMAGE = None

    global GLOBAL_DATASET
    GLOBAL_DATASET = []

    global GLOBAL_LATLNG
    GLOBAL_LATLNG = LatLng()