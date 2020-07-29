import time
import pynmea2
import RPi.GPIO as GPIO
from threading import Thread
from serial import Serial
from hcsr04sensor import sensor as hcsr04


GPIO.setmode(GPIO.BCM)
#超音波模組
class HCSR04(Thread):
    def __init__(self, trigger_pin, echo_pin):
        Thread.__init__(self)

        self.TRIGGER_PIN = trigger_pin
        self.ECHO_PIN = echo_pin
        self._distance = None

    def run(self):
        while True:
            try:
                sr04 = hcsr04.Measurement(self.TRIGGER_PIN, self.ECHO_PIN)
                raw_measurement = sr04.raw_distance()
                distance = sr04.distance_metric(raw_measurement)
            except UnboundLocalError:
                self._distance = None
                continue

            print(f'超音波模組偵測到距離為 {distance}cm')
            self._distance = distance

            time.sleep(1)

    @property
    def distance(self):
        return self._distance


#GPS模組
class GPS(Thread):
    def __init__(self, port = '/dev/ttyAMA0'):
        self._port = port
        self._lat = None
        self._lng = None

    def run(self):
        while True:
            ser = Serial(self._port, baudrate=9600, timeout=0.5)
            new_data = ser.readline()
            
            if new_data[:6] == '$GPRMC':
                new_msg = pynmea2.parse(new_data)
                lat = new_msg.latitude
                lng = new_msg.longitude
                
                print(f'Latitude: {str(lat)}, Longitude: {str(lng)}')
                self._lat = str(lat)
                self._lng = str(lng)

                time.sleep(1)

    def latlng(self):
        return self._lat, self._lng

    @property
    def latitude(self):
        return self._lat

    @property
    def longitude(self):
        return self._lng


#六自由度感測模組
class LSM6DS3(Thread):
    def __init__(self):
        Thread.__init__(self)


def destroy_sensors():
    GPIO.cleanup()