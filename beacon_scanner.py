import time
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

    def run(self):
        while True:
            devices = self._scanner.scan(timeout = 10.0)

            for dev in devices:
                print(f'Device {dev.addr} ({dev.addrType}), RSSI={dev.rssi} dB')

                for adtype, desc, value in dev.getScanData():
                    print(f'  {desc} = {value}')


            time.sleep(10)