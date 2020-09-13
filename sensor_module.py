import time
import math
import smbus
import pynmea2
import RPi.GPIO as GPIO
from threading import Thread
from enum import IntEnum
from serial import Serial
from hcsr04sensor import sensor as hcsr04

import utils


GPIO.setmode(GPIO.BCM)
# 超音波模組
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
            except (UnboundLocalError, SystemError):
                self._distance = None
                continue

            utils.GLOBAL_LOGGER.info(f'超音波模組偵測到距離為 {distance}cm')
            self._distance = distance

            time.sleep(1)

    @property
    def distance(self):
        return self._distance


# GPS模組
class GPS(Thread):
    def __init__(self, port = '/dev/ttyAMA0'):
        Thread.__init__(self)

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
                
                utils.GLOBAL_LOGGER.info(f'latitude: {str(lat)}, longitude: {str(lng)}')
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


# 陀螺儀與加速度感測模組
class MPU6050(Thread):
    def __init__(self):
        Thread.__init__(self)
        
        self._bus = smbus.SMBus(1)
        self._power_mgmt = 0x6b
        self._address = 0x68

        self._gyroskop_xout = None
        self._gyroskop_yout = None
        self._gyroskop_zout = None
        
        self._beschleunigung_xout = None
        self._beschleunigung_yout = None
        self._beschleunigung_zout = None

        self._x_rotation = None
        self._y_rotation = None

    def _read_byte(self, reg):
        return self._bus.read_byte_data(self._address, reg)
    
    def _read_word(self, reg):
        h = self._read_byte(reg)
        l = self._read_byte(reg + 1)
        value = (h << 8) + l
        return value
    
    def _read_word_2c(self, reg):
        val = self._read_word(reg)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val
    
    def _dist(self, a,b):
        return math.sqrt((a * a) + (b * b))
    
    def _get_y_rotation(self, x, y, z):
        radians = math.atan2(x, self._dist(y, z))
        return -math.degrees(radians)
    
    def _get_x_rotation(self, x, y, z):
        radians = math.atan2(y, self._dist(x, z))
        return math.degrees(radians)

    def run(self):
        while True:
            try:
                self._bus.write_byte_data(self._address, self._power_mgmt, 0)

                gyroskop_xout = self._read_word_2c(0x43)
                gyroskop_yout = self._read_word_2c(0x45)
                gyroskop_zout = self._read_word_2c(0x47)

                beschleunigung_xout = self._read_word_2c(0x3b)
                beschleunigung_yout = self._read_word_2c(0x3d)
                beschleunigung_zout = self._read_word_2c(0x3f)
            except OSError:
                time.sleep(1)
                continue

            print('Gyroskop')
            print('--------')

            gyroskop_xout_skaliert = gyroskop_xout / 131
            gyroskop_yout_skaliert = gyroskop_yout / 131
            gyroskop_zout_skaliert = gyroskop_zout / 131

            print('gyroskop_xout: ', ('%5d' % gyroskop_xout), ' skaliert: ', gyroskop_xout_skaliert)
            print('gyroskop_yout: ', ('%5d' % gyroskop_yout), ' skaliert: ', gyroskop_yout_skaliert)
            print('gyroskop_zout: ', ('%5d' % gyroskop_zout), ' skaliert: ', gyroskop_zout_skaliert)
            
            self._gyroskop_xout = gyroskop_xout
            self._gyroskop_yout = gyroskop_yout
            self._gyroskop_zout = gyroskop_zout

            print()
            print('Beschleunigungssensor')
            print('---------------------')

            beschleunigung_xout_skaliert = beschleunigung_xout / 16384.0
            beschleunigung_yout_skaliert = beschleunigung_yout / 16384.0
            beschleunigung_zout_skaliert = beschleunigung_zout / 16384.0

            print('beschleunigung_xout: ', ('%6d' % beschleunigung_xout), ' skaliert: ', beschleunigung_xout_skaliert)
            print('beschleunigung_yout: ', ('%6d' % beschleunigung_yout), ' skaliert: ', beschleunigung_yout_skaliert)
            print('beschleunigung_zout: ', ('%6d' % beschleunigung_zout), ' skaliert: ', beschleunigung_zout_skaliert)

            self._beschleunigung_xout = beschleunigung_xout
            self._beschleunigung_yout = beschleunigung_yout
            self._beschleunigung_zout = beschleunigung_zout

            x_rotation = self._get_x_rotation(beschleunigung_xout_skaliert, beschleunigung_yout_skaliert, beschleunigung_zout_skaliert)
            y_rotation = self._get_y_rotation(beschleunigung_xout_skaliert, beschleunigung_yout_skaliert, beschleunigung_zout_skaliert)

            print('X Rotation: ' , x_rotation)
            print('Y Rotation: ' , y_rotation)
            print('-----------------------------------')

            self._x_rotation = x_rotation
            self._y_rotation = y_rotation

            time.sleep(1)

    def _skaliert(self, value, scale):
        return value / scale

    def gyroskop(self, skaliert = True):
        scale = 131
        gyroskop = {
            'x': self._gyroskop_xout,
            'y': self._gyroskop_yout,
            'z': self._gyroskop_zout
        }

        if skaliert:
            for axis in ('x', 'y', 'z'):
                gyroskop[axis] = self._skaliert(gyroskop[axis], scale)

        return gyroskop

    def beschleunigungssensor(self, skaliert = True):
        scale = 16384.0
        beschleunigungssensor = {
            'x': self._beschleunigung_xout,
            'y': self._beschleunigung_yout,
            'z': self._beschleunigung_zout
        }

        if skaliert:
            for axis in ('x', 'y', 'z'):
                beschleunigungssensor[axis] = \
                    self._skaliert(beschleunigungssensor[axis], scale)

        return beschleunigungssensor

    def rotation(self):
        return {
            'x': self._x_rotation,
            'y': self._y_rotation
        }


# 蜂鳴器
class Buzzer:
    def __init__(self, buzzer_pin):
        self.BUZZER_PIN = buzzer_pin

    def _play(self, pitch, duration):
        period = 1.0 / pitch
        delay = period / 2
        cycles = int(duration * pitch)

        for _ in range(cycles):
            GPIO.output(self.BUZZER_PIN, True)
            time.sleep(delay)
            GPIO.output(self.BUZZER_PIN, False)
            time.sleep(delay)

    def buzz(self, frequency, duration = 1, repeat = 0):
        if isinstance(frequency, (int, float)):
            frequency = [frequency for i in range(repeat + 1)]

        if isinstance(duration, (int, float)):
            duration = [duration for i in range(len(frequency))]

        GPIO.setup(self.BUZZER_PIN, GPIO.OUT)
        for i, f in enumerate(frequency):
            self._play(f, duration[i])
            time.sleep(duration[i] * 0.5)
        

class Frequency(IntEnum):
    ALERT = 784
    ALARM = 1568


# 緊急按鈕
class EmergencyButton(Thread):
    def __init__(self, button_pin, service):
        Thread.__init__(self)

        self._service = service
        self.BUTTON_PIN = button_pin
        GPIO.add_event_detect(button_pin, GPIO.FALLING, 
            callback = self.btn_press, bouncetime = 200)

    def btn_press(self):
        timer = utils.AsyncTimer()
        timer.start()

        while GPIO.input(self.BUTTON_PIN) == 0:
            timer.stop()

        if timer.elapsed_time >= 1:
            content = utils.GLOBAL_SPEECH_CONTENT
            self._service.push_notification(f'緊急狀況: {content}')
        else:
            self._service.cancel = True

        time.sleep(1)


def destroy_sensors():
    GPIO.cleanup()