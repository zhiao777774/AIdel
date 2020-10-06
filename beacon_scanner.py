import time
import math
from threading import Thread
from bluepy.btle import Scanner, DefaultDelegate

import utils


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            utils.GLOBAL_LOGGER.info(f'Discovered Device {dev.addr}')
        elif isNewData:
            utils.GLOBAL_LOGGER.info(f'Recieved New Data from {dev.addr}')


class BeaconScanner(Thread):
    def __init__(self):
        Thread.__init__(self)

        self._scanner = Scanner().withDelegate(ScanDelegate())
        self._strength = 59
        self._attenuation = 2.0

        self.data = dict()

    def run(self):
        while True:
            self.data.clear()
            devices = self._scanner.scan(timeout = 10.0)

            for dev in devices:
                print(f'Device {dev.addr} ({dev.addrType}), RSSI={dev.rssi} dB')
                self.data[dev.addr] = {}
                
                rssi = abs(int(dev.rssi))
                distance = math.pow(10, (rssi - self._strength) / (10 * self._attenuation))
                self.data[dev.addr]['distance'] = distance

                for adtype, desc, value in dev.getScanData():
                    print(f'  {desc} = {value}')
                    self.data[dev.addr][desc] = value


            time.sleep(10)