import os
import serial
import time
import json
from threading import Thread

from .infrared_sensor import InfraredSensor


class Chatbot(Thread):
    def __init__(self, port):
        Thread.__init__(self)

        self._send_data = None
        self._seri_port = serial.Serial(port, baudrate = 9600, timeout = 1.0)

        action_data_path = f'{os.path.dirname(os.path.realpath(__file__))}/chatbot-action.json'
        with open(action_data_path , 'r', encoding = 'UTF-8') as reader:
            self._action_data = json.loads(reader.read())

        InfraredSensor(port = self._seri_port, func = self._infrared_control).start()

    def run(self):
        while True:
            msg = self._send_data or ''

            if msg in ('close', 'stop'):
                data = self._action_data['stop']
                self._seri_port.write(str(data['number']).encode())
                break
            elif self._action_data[msg]:
                data = self._action_data[msg]
                self._seri_port.write(str(data['number']).encode())

                time.sleep(data['sleeptime'] / 1000)
            else:
                time.sleep(1)

    def _infrared_control(self, signal):
        data = None
        
        if 'FFC23D' in signal:  # 右鍵
            data = self._action_data['>']
        elif 'FF22DD' in signal:  # 左鍵
            data = self._action_data['<']
        elif 'FF629D' in signal:  # 上鍵
            data = self._action_data['^']
        elif 'FFA857' in signal:  # 下鍵
            data = self._action_data['v']
        elif 'FF02FD' in signal:  # OK鍵
            data = self._action_data['stop']
        else: return

        number = str(data['number'])
        sleep_time = data['sleeptime']
        self._seri_port.write(number.encode())

        if sleep_time > 1000:
            time.sleep((sleep_time - 1000) / 1000)

    def act(self, msg):
        self._send_data = msg