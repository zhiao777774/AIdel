import time
from threading import Thread
from apscheduler.schedulers.blocking import BlockingScheduler

from .db_handler import MongoDB, np_cvt_base64img


class GuardianshipService(Thread):
    def __init__(self, interval):
        Thread.__init__(self)

        self.data = dict()
        self._interval = interval
        self._sched = BlockingScheduler()
        
    def run(self):
        period = ''
        for t in range(0, 60, self._interval):
            period += f'{t}{"," if t != 60 - self._interval else ""}'

        self._sched.add_job(self._save, 'cron', minute = period, id = 'save_image_job')
        self._sched.start()

    def _save(self):
        with MongoDB('120.125.83.10', '8080') as db:
            t = time.localtime()
            fdate = time.strftime('%Y/%m/%d', t)
            ftime = f'{t.tm_hour}:{"00" if t.tm_min < 30 else "30"}'

            image = self.data['image']
            lat = self.data['lat']
            lng = self.data['lng']
            address = self.data['address']

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
                insert_data['data'] += data['data']
                insert_data['locations'] += data['locations']
                db.insert({
                    'collection': 'historicalImage',
                    'data': insert_data
                })

            db.select({
                'collection': 'historicalImage',
                'filter': { 'date': fdate }
            }, _insert)
        
    def destroy(self):
        self._sched.remove_job('save_image_job')