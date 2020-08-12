import time
import requests
from threading import Thread
from apscheduler.schedulers.blocking import BlockingScheduler

from .db_handler import MongoDB, np_cvt_base64img
from .sensor_module import Buzzer


class GuardianshipService(Thread):
    def __init__(self, interval):
        Thread.__init__(self)

        self.data = dict()
        self.mpu = None
        self._interval = interval
        self._sched = BlockingScheduler()
        
    def run(self):
        period = ''
        for t in range(0, 60, self._interval):
            period += f'{t}{"," if t != 60 - self._interval else ""}'

        self._sched.add_job(self._save, 'cron', minute = period, id = 'save_image_job')
        self._sched.start()

        buzzer = Buzzer(buzzer_pin = 16)
        while True:
            if not self.mpu: continue 

            accel = self.mpu.beschleunigungssensor()
            if accel['z'] <= 0:
                print('疑似發生跌倒!')
                buzzer.buzz(698, 0.5)
                buzzer.buzz(523, 0.5)

            time.sleep(1)

    def _save(self):
        if not self.data: return

        with MongoDB('120.125.83.10', '8080') as db:
            t = time.localtime()
            fdate = time.strftime('%Y/%m/%d', t)
            ftime = f'{t.tm_hour}:{"00" if t.tm_min < 30 else "30"}'

            image = self.data['image']
            lat = self.data['lat']
            lng = self.data['lng']
            address = latlng_query_addr(lat = lat, lng = lng)

            insert_data = {
                'date': fdate,
                'data': [{
                    'time': ftime,
                    'data': [{
                        'id': t.tm_min / 6,
                        'image': np_cvt_base64img(image),
                        'description': address
                    }]
                }],
                'locations': [{
                    'latitude': lat,
                    'longitude': lng
                }]
            }

            def _insert(data):
                insert_data['locations'] += data['locations']

                l = [i for i, d in enumerate(data['data']) if d['time'] == ftime]
                if l:
                    index = l[0]
                    insert_data['data'][0]['data'] += data['data'][index]['data']
                else:
                    insert_data['data'] += data['data']

                db.insert({
                    'collection': 'historicalImage',
                    'data': insert_data
                })

            db.select({
                'collection': 'historicalImage',
                'filter': { 'date': fdate }
            }, _insert)
        
    def stop(self):
        self._sched.remove_job('save_image_job')


def latlng_query_addr(lat, lng, buffer=150):
    service_url = 'https://addr.tgos.tw/addrws/v40/GeoQueryAddr.asmx/PointQueryAddr'
    params = {
        'oAPPId': '',
        'oAPIKey': '',
        'oPX': lng, 
        'oPY': lat, 
        'oBuffer': buffer,
        'oSRS': 'EPSG:4326',
        'oResultDataType': 'JSON'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.get(service_url, params = params, headers = headers)
    address = ''
    if response.status_code == 200:
        res = response.json()

    return address