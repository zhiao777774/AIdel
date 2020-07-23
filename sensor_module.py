import time
import RPi.GPIO as GPIO
from threading import Thread
from hcsr04sensor import sensor as hcsr04


#超音波模組
class HCSR04(Thread):
    def __init__(self, trigger_pin, echo_pin):
        Thread.__init__(self)

        self.TRIGGER_PIN = trigger_pin
        self.ECHO_PIN = echo_pin
        self._distance = -1

    def run(self):
        while True:
            sr04 = hcsr04.Measurement(self.TRIGGER_PIN, self.ECHO_PIN)
            raw_measurement = sr04.raw_distance()
            distance = sr04.distance_metric(raw_measurement)

            print(f'超音波模組偵測到距離為 {distance}cm')
            self._distance = distance

            time.sleep(1)

    @property
    def distance(self):
        return self._distance
            

#六自由度感測模組
class LSM6DS3(Thread):
    def __init__(self):
        Thread.__init__(self)


def destroy_sensors():
    GPIO.cleanup()