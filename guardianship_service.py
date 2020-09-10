import time
import requests
from threading import Thread
from apscheduler.schedulers.blocking import BlockingScheduler

from .image_processor import np_cvt_base64img
from .db_handler import MongoDB
from .utils import AsyncTimer


class GuardianshipService(Thread):
    def __init__(self, interval):
        Thread.__init__(self)

        self.data = dict()
        self.mpu = None
        self.buzzer = None
        self.speech = ''
        self._cancel = False

        self._interval = interval
        self._sched = BlockingScheduler()
        
    def run(self):
        period = ''
        for t in range(0, 60, self._interval):
            period += f'{t}{"," if t != 60 - self._interval else ""}'

        self._sched.add_job(self._save, 'cron', minute = period, id = 'save_image_job')
        self._sched.start()

        timer = AsyncTimer()
        pushed = False
        while True:
            if not self.mpu or self._cancel:
                timer.stop()
                time.sleep(1)
                continue 

            accel = self.mpu.beschleunigungssensor()
            if accel['z'] <= 0.1:
                print('疑似發生跌倒!')
                timer.start()

                if timer.elapsed_time >= 15 and not pushed:
                    print('發送緊急推播!')
                    self.push_notification(noti_type = '跌倒')
                    pushed = True
                else: 
                    self.buzzer.buzz(698, 0.5)
                    self.buzzer.buzz(523, 0.5)
            else:
                print('解除跌倒警報!')
                timer.stop()
                pushed = False

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

    def push_notification(self, noti_type):
        if not self.data: return
        if not isinstance(noti_type, str): return

        with MongoDB('120.125.83.10', '8080') as db:
            t = time.localtime()
            date = time.strftime('%Y/%m/%d %H:%M', t)
            lat = self.data['lat']
            lng = self.data['lng']
            address = latlng_query_addr(lat = lat, lng = lng)

            db.insert({
                'collection': 'historicalAccident',
                'data': {
                    'date': date,
                    'type': noti_type,
                    'location': {
                        'address': address,
                        'latitude': lat,
                        'longitude': lng
                    }
                }
            })
        
    def stop(self):
        self._sched.remove_job('save_image_job')

    @property
    def cancel(self):
        return self._cancel

    @cancel.setter
    def cancel(self, cancel):
        if cancel == self._cancel: return

        self._cancel = cancel
        if cancel:
            timer = AsyncTimer()
            timer.start()

            if timer.elapsed_time >= 10:
                self._cancel = False
                timer.stop()


def latlng_query_addr(lat, lng, buffer=150):
    service_url = 'http://120.125.83.10:8090/latlngQueryAddress'
    post_data = {
        'lat': lat,
        'lng': lng, 
        'buffer': buffer,
    }

    response = requests.post(service_url, json = post_data)
    address = ''
    if response.status_code == 200:
        address = response.json()['result']

    return address