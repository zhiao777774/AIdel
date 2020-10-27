import time
from threading import Thread


class InfraredSensor(Thread):
    def __init__(self, port, func):
        Thread.__init__(self)

        self._seri_port = port
        self._agent = func

        self.setDaemon(True)

    def run(self):
        while True:
            while self._seri_port.in_waiting:
                break

            raw_data = self._seri_port.readline()
            data = raw_data.decode('ISO-8859-1')

            self._agent(data)

            time.sleep(1)