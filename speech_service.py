import abc
import os
import shutil
import time
import math
import re
import requests
import wave
import pyaudio
import speech_recognition as sr
import jieba
import jieba.analyse
import googlemaps
import pygame
from threading import Thread
from xml.etree import ElementTree
from enum import Enum

import utils
import file_controller as fc
from .word_vector_machine import find_synonyms
from .translator import translate
# from .text_recognizer import text_recognize


class AbstractService:
    @abc.abstractmethod
    def execute(self, service, keyword):
        return NotImplemented


class ServiceType(Enum):
    SEARCH = '尋找'
    WHETHER = '有沒有'
    NAVIGATION = '導航'

    @classmethod
    def get_service(cls, service):
        GMAPS_KEY = 'AIzaSyC0NXEeivr01yTkj3vOcEXUFYJwvv32bMU'

        return {
            cls.SEARCH.value: Searcher(),
            cls.WHETHER.value: GoogleService(GMAPS_KEY),
            cls.NAVIGATION.value: GoogleService(GMAPS_KEY)
        }.get(service)


class SpeechService(Thread):
    def __init__(self):
        Thread.__init__(self)
        os.mkdir(f'{fc.AUDIO_PATH}/temp')

        dict_path = f'{fc.ROOT_PATH}/data/dict.txt.big.txt'
        jieba.set_dictionary(dict_path)

        keywords_path = f'{fc.ROOT_PATH}/data/triggerable_keywords.json'
        self._triggerable_keywords = fc.read_json(keywords_path)

        self._mode = dict()
        self._mode[ServiceType.NAVIGATION.name] = False
        self._mode[ServiceType.SEARCH.name] = False

        self._service = dict()
        self._service[ServiceType.NAVIGATION.name] = None
        self._service[ServiceType.SEARCH.name] = None

    def run(self):
        while True:
            print('Recording...')
            sentence = self.voice2text()
            utils.GLOBAL_SPEECH_CONTENT = sentence
            '''
            keywords = [k for k in self._triggerable_keywords if k in sentence]
            triggerable = len(keywords) > 0
            if not triggerable:
                continue

            for k in keywords:
                sentence = _replace_and_trim(sentence, k)
            '''
            if sentence == '無法翻譯': continue
            elif sentence in ('取消導航', '停止導航', '取消尋找', '停止尋找'):
                mode = sentence[2:]
                if mode == '導航' and self._mode[ServiceType.NAVIGATION.name]:
                    utils.GLOBAL_LOGGER.info(f'正在停止{mode}')
                    self.response(f'正在停止{mode}.wav')
                    self._mode[ServiceType.NAVIGATION.name] = False
                    self._service[ServiceType.NAVIGATION.name].exit = True
                    self._service[ServiceType.NAVIGATION.name] = None
                elif mode == '尋找' and self._mode[ServiceType.SEARCH.name]:  
                    utils.GLOBAL_LOGGER.info(f'正在停止{mode}')
                    self.response(f'正在停止{mode}.wav')
                    self._mode[ServiceType.SEARCH.name] = False
                    self._service[ServiceType.SEARCH.name].exit = True
                    self._service[ServiceType.SEARCH.name] = None
                else:
                    utils.GLOBAL_LOGGER.info(f'{mode}功能未開啟')
                    self.response(f'{mode}功能未開啟.wav')
                continue
            elif sentence in ('這是什麼', '這個是什麼'):
                print('正在辨識中')
                self.response(f'正在辨識中.wav')
                
                results = []
                # results = text_recognize(utils.GLOBAL_IMAGE)
                # results = [map(lambda s: _replace_and_trim(s, ' '), results)]
                # results = self.extract_keywords(results)
                # results = self.filter_keywords(results, 5)
                # results = [tag for tag, _ in results]

                keyword = ''.join(results)
                response = f'這個是{keyword}'
                utils.GLOBAL_LOGGER.info(response)
                async_play_audio(response, responser = Responser(load = False))
                continue

            service = [k for k in ServiceType if k.value in sentence]
            words = self.sentence_segment(sentence)
            keywords = self.extract_keywords(words)
            keywords = self.filter_keywords(keywords, 5)

            for tag, weight in keywords:
                print(f'{tag} , {str(weight)}')

            confidences = [conf for _, conf in keywords]
            keywords = [tag for tag, _ in keywords]

            if not service:
                for i, tag in enumerate(keywords):
                    try:
                        synonyms = list(map(lambda s: s[0], find_synonyms(tag)))
                    except KeyError: continue
                    results = [k for k in ServiceType if k.value in synonyms]
                    if results: 
                        service = results

                        temp = []
                        for j, tag in enumerate(keywords):
                            temp.append(results[0].value if j == i else tag)
                        keywords = temp
                        break

                if not service:
                    print('對不起，請您再說一次')
                    self.response('對不起，請您再說一次.wav')
                    continue
            elif (ServiceType.NAVIGATION in service) & (len(service) >= 2):
                print('對不起，請您再說一次')
                self.response('對不起，請您再說一次.wav')
                continue

            service = service[1 if len(service) >= 2 else 0]
            try:
                service, place = self.finds(keywords, confidences, service.value)
            except (IndexError, ValueError): 
                print('對不起，請您再說一次')
                self.response('對不起，請您再說一次.wav')
                continue
            print(f'Question: {service}->{place}')

            if service == ServiceType.NAVIGATION.value and \
                self._mode[ServiceType.NAVIGATION.name]:
                utils.GLOBAL_LOGGER.info('導航功能啟動中')
                self.response('導航功能啟動中.wav')
                continue
            if service == ServiceType.SEARCH.value and \
                self._mode[ServiceType.SEARCH.name]:
                utils.GLOBAL_LOGGER.info('尋找功能啟動中')
                self.response('尋找功能啟動中.wav')
                continue

            try:
                result = ServiceType.get_service(service).execute(service, place)
            except: 
                print('功能錯誤，請再試一次')
                self.response('功能錯誤，請再試一次.wav')
                continue
            if service == ServiceType.WHETHER.value:
                response = f'附近{"有" if result else "沒有"}{place}'
                print(f'-> {response}')
                self.response(response)
            elif service == ServiceType.NAVIGATION.value:
                if not result:
                    print(f'-> 無法導航至{place}')
                    self.response(f'無法導航至{place}')
                    continue

                utils.GLOBAL_LOGGER.info(f'正在取得到{place}的路線')
                self.response(f'正在取得到{place}的路線')

                navigator = Navigator(**result, destination = place)
                navigator.setDaemon(True)
                navigator.start()

                self._mode[ServiceType.NAVIGATION.name] = True
                self._service[ServiceType.NAVIGATION.name] = navigator
            elif service == ServiceType.SEARCH.value:
                if result:
                    utils.GLOBAL_LOGGER.info(f'開始幫您尋找{place}')
                    self.response(f'開始幫您尋找{place}')

                    searcher = result
                    searcher.setDaemon(True)
                    searcher.start()

                    self._mode[ServiceType.SEARCH.name] = True
                    self._service[ServiceType.SEARCH.name] = searcher
                else:
                    print('對不起，請您再說一次')
                    self.response('對不起，請您再說一次.wav')

    def response(self, text):
        resp = Responser(load = False)

        if not os.path.isfile(f'{fc.AUDIO_PATH}/{text}'):
            async_play_audio(text, responser = resp)
        else:
            resp.play_audio(text)

    def voice2text(self):
        audio = None
        text = None

        # self._record_wave()
        device = self.get_device()
        r = sr.Recognizer()
        with sr.Microphone(device_index=device['index']) as source:
            r.adjust_for_ambient_noise(source)
            try:
                audio = r.listen(source, timeout = 5)
            except sr.WaitTimeoutError:
                text = '無法翻譯'
                print(text)
                return text
        '''
        r = sr.Recognizer()
        with sr.AudioFile('record.wav') as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        '''
        try:
            text = r.recognize_google(audio, language='zh-TW')
        except (sr.UnknownValueError, sr.RequestError):
            text = '無法翻譯'

        print(text)
        return text

    def _record_wave(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        RATE = 16000
        CHANNELS = 1
        RECORD_SECONDS = 5

        pa = pyaudio.PyAudio()
        stream = pa.open(format=FORMAT,
                         channels=CHANNELS,
                         rate=RATE,
                         input=True,
                         frames_per_buffer=CHUNK)
        print('Recording...')
        buffer = []
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            audio_data = stream.read(CHUNK, exception_on_overflow=False)
            buffer.append(audio_data)
        print('Record Done')
        stream.stop_stream()
        stream.close()
        pa.terminate()
        wf = wave.open('record.wav', 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pa.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(buffer))
        wf.close()

    def sentence_segment(self, sentence):
        return jieba.lcut(sentence)

    def extract_keywords(self, words):
        keywords = []
        for word in words:
            tags = jieba.analyse.extract_tags(word, topK=5, withWeight=True)
            if tags:
                keywords.append(tags[0])
        return keywords

    def filter_keywords(self, keywords, threshold=10):
        return [k for k in keywords if k[1] >= threshold]

    def finds(self, keywords, confidences, keyword):
        if isinstance(keywords[0], tuple):
            keywords = list(map(lambda k: k[0], keywords))

        index = keywords.index(keyword)
        place = None

        if len(keywords) == 2:
            place = keywords[0 if index else 1]
        else:
            keywords.remove(keyword)
            confidences.pop(index)
            keywords = [k for _, k in sorted(
                zip(confidences, keywords), reverse = True)]

            place = keywords[0]

        return (keyword, place)

    def get_device(self):
        pa = pyaudio.PyAudio()
        return pa.get_default_input_device_info()


def _replace_and_trim(text, old, new=''):
    return text.replace(old, new).strip()

def async_play_audio(text, remove = True, responser = None):
    responser = responser or Responser(load = False)
    if not isinstance(responser, Responser):
        responser = Responser(load = False)

    t = Thread(target = responser.tts, 
        args = (text, f'{fc.AUDIO_PATH}/temp/{text}'))
    t.start()
    t.join()

    if remove:
        class Remover(Thread):
            def __init__(self):
                Thread.__init__(self)

            def run(self):
                while True:
                    try: 
                        os.remove(f'{fc.AUDIO_PATH}/temp/{text}.wav')
                        break
                    except PermissionError: time.sleep(1)

        def _remove_audio():
            Remover().start()

        responser.play_audio(f'temp/{text}.wav', callback = _remove_audio)


class TextToSpeech:
    def __init__(self, subscription_key, region_identifier, input_text):
        self.subscription_key = subscription_key
        self.region_identifier = region_identifier
        self.tts = input_text
        self.timestr = time.strftime('%Y%m%d-%H%M')
        self.access_token = self._get_token()

    def _get_token(self):
        fetch_token_url = f'https://{self.region_identifier}.api.cognitive.microsoft.com/sts/v1.0/issueToken'
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        return str(response.text)

    def save_audio(self, audio_name = ''):
        base_url = f'https://{self.region_identifier}.tts.speech.microsoft.com/'
        path = 'cognitiveservices/v1'
        constructed_url = base_url + path
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': 'AIdel'
        }
        xml_body = ElementTree.Element('speak', version='1.0')
        xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', 'zh-TW')
        voice = ElementTree.SubElement(xml_body, 'voice')
        voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'zh-TW')
        voice.set(
            'name', 'Microsoft Server Speech Text to Speech Voice (zh-TW, Yating, Apollo)')
        voice.text = self.tts
        body = ElementTree.tostring(xml_body)

        response = requests.post(constructed_url, headers=headers, data=body)
        if response.status_code == 200:
            audio_name = audio_name or self.tts
            with open(audio_name + '.wav', 'wb') as audio:
                audio.write(response.content)
                print('\nStatus code: ' + str(response.status_code) +
                      '\nYour TTS is ready for playback.\n')
        else:
            print('\nStatus code: ' + str(response.status_code) +
                  '\nSomething went wrong. Check your subscription key and headers.\n')


class Responser:
    def __init__(self, load = True):
        if load:
            self._response = fc.read_json(f'{fc.ROOT_PATH}/data/response.json')
        else:
            self._response = None

    def decide_response(self, keyword):
        if not self._response: return
        res = self._response

        direction, distance = keyword.split(',')
        keyword = direction

        if direction == '^':
            for t in (30, 50, 100):
                if float(distance) <= t:
                    keyword = f'^{t}'
                    break
        elif direction in ('<', '>'):
            for t in (50, 100, 150, 200):
                if float(distance) <= t:
                    keyword = f'{direction}{t}'
                    break

        return res[keyword]

    def play_audio(self, audio_name, callback = None):
        if utils.AUDIO_PLAYING: 
            priority = int(audio_name not in self._response.values())
            utils.AUDIO_QUEUE.put((priority, audio_name, callback))
            utils.GLOBAL_LOGGER.info(f'「{audio_name}」已加入至播放佇列中')
            return

        utils.AUDIO_PLAYING = True

        pygame.mixer.init()
        pygame.mixer.music.load(f'{fc.ROOT_PATH}/data/audio/{audio_name}')
        
        try:
            pygame.mixer.music.play()
        except:
            utils.AUDIO_PLAYING = False
            self.play_audio(audio_name, callback)

        while pygame.mixer.music.get_busy(): continue

        pygame.mixer.quit()
        if callable(callback): callback()

        utils.AUDIO_PLAYING = False
        if not utils.AUDIO_QUEUE.empty():
            _, audio_name, callback = utils.AUDIO_QUEUE.get()
            utils.GLOBAL_LOGGER.info(f'已從播放佇列取出「{audio_name}」')

            self.play_audio(audio_name, callback)

    def tts(self, input_text, audio_name = ''):
        subscription_key = '037a6e1532d6499dbdbfb09c1d4276bb'
        region_identifier = 'southcentralus'
        app = TextToSpeech(subscription_key, region_identifier, input_text)
        app.save_audio(audio_name)


class GoogleService(AbstractService):
    def __init__(self, gmaps_key):
        self._gmaps_key = gmaps_key
        self._gmaps = googlemaps.Client(key = gmaps_key)
    
    def places_nearby(self, latlng, type_, radius = 150):
        radarResults = self._gmaps.places_nearby(location = latlng, 
                                          radius = radius, 
                                          type = type_)
        return radarResults['results']

    def places_radar(self, latlng, type_, radius = 150):
        service_url = 'https://maps.googleapis.com/maps/api/place/textsearch/'
        result_type = 'json'
        constructed_url = service_url + result_type
        params = {
            'key': self._gmaps_key,
            'query': type_,
            'location': ','.join(map(lambda c: str(c), latlng)),
            'radius': radius,
            'language': 'zh-TW'
        }

        response = requests.get(constructed_url, params=params)
        results = []
        if response.status_code == 200:
            res = response.json()
            # next_page_token = res['next_page_token']
            res = res['results'][:5]

            if len(res) > 0:
                for item in res:
                    location = item['geometry']['location']
                    results.append({
                        'name': item['name'],
                        'address': item['formatted_address'],
                        'latitude': location['lat'],
                        'longitude': location['lng']
                    })

        print(f'Queried: {results}')
        return results
    
    def navigate(self, start, destination):
        service_url = 'https://maps.googleapis.com/maps/api/directions/'
        result_type = 'json'
        constructed_url = service_url + result_type
        params = {
            'key': self._gmaps_key,
            'origin': ','.join(map(lambda c: str(c), start)),
            'destination': ','.join(map(lambda c: str(c), destination)),
            'mode': 'walking',
            'language': 'zh-TW'
        }

        response = requests.get(constructed_url, params=params)
        result = {}
        if response.status_code == 200:
            res = response.json()
            leg = res['routes'][0]['legs'][0]

            if leg:
                result['distance'] = leg['distance']['value']
                result['duration'] = leg['duration']['value']
                result['start_location'] = dict(
                    **leg['start_location'], address = leg['start_address'])
                result['end_location'] = dict(
                    **leg['end_location'], address = leg['end_address'])
                result['routes'] = []

                html_cleaner = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
                for step in leg['steps']:
                    result['routes'].append({
                        'distance': step['distance']['value'],
                        'duration': step['duration']['value'],
                        'instruction': re.sub(html_cleaner, '', step['html_instructions']),
                        'start_location': step['start_location'],
                        'end_location': step['end_location']
                    })

        print(f'Queried: {result}')
        return result

    def execute(self, service, keyword):
        # lat = utils.GLOBAL_LATLNG.latitude
        # lng = utils.GLOBAL_LATLNG.longitude
        lat = 25.0040133
        lng = 121.3427151

        if service == ServiceType.WHETHER.value:
            return self.places_radar(latlng = (lat, lng), type_ = keyword)
        elif service == ServiceType.NAVIGATION.value:
            neighborhoods = self.places_radar(latlng = (lat, lng), type_ = keyword)

            if neighborhoods:
                neighborhood = neighborhoods[0]
                start = (lat, lng)
                destination = (neighborhood['latitude'], neighborhood['longitude'])
                return self.navigate(start = start, destination = destination)
            else:
                return None
        else:
            return None


class Searcher(AbstractService, Thread):
    def __init__(self):
        Thread.__init__(self)

        self._keyword = None
        self.exit = False

        utils.GLOBAL_LOGGER.info('Searcher is started.')

    def execute(self, service, keyword):
        keyword = translate(keyword, source = 'zh-TW', target = 'EN')
        self._keyword = keyword.lower()
        return self

    def run(self):
        resp = Responser(load = False)

        while True:
            if self.exit: break

            objs = utils.GLOBAL_DATASET
            if objs:
                filtered = [o for o in objs if o.clsName != 'unknown']
                k = [o for o in filtered if o.clsName.lower() == self._keyword]
                # k = [o for o in filtered if
                #         translate(o.clsName, source = 'EN', target = 'zh-TW') == self._keyword]

                if not k:
                    translated = [map(lambda o: o.clsName.lower(), filtered)]
                    # translated = [map(lambda o: translate(
                    #         o.clsName, source = 'EN', target = 'zh-TW'), filtered)]

                    for i, phrase in enumerate(translated):
                        synonyms = list(map(lambda s: s[0], find_synonyms(phrase)))
                        if self._keyword in synonyms:
                            k = [filtered[i]]
                            break

                    if not k:
                        time.sleep(1)
                        continue

                text = f'已找到{self._keyword}'
                text += f'，位於您前方{round(k[0].distance / 100)}公尺處'
                utils.GLOBAL_LOGGER.info(text)

                async_play_audio(text, responser = resp)
                break

            time.sleep(1)


class Navigator(Thread):
    def __init__(self, **kwargs):
        Thread.__init__(self)
        self.__dict__.update(kwargs)
        self.exit = False

        utils.GLOBAL_LOGGER.info('Navigator is started.')

    def run(self):
        resp = Responser(load = False)
        utils.GLOBAL_LOGGER.info(f'開始導航至{self.destination}')
        async_play_audio(f'開始導航至{self.destination}', responser = resp)
        

        for route in self.routes:
            if self.exit: break

            distance = math.ceil(route['distance'])
            steps = math.ceil(distance / 61)
            duration = math.ceil(distance / 0.92)
            text = f'{route["instruction"]}，約走{distance}公尺'

            async_play_audio(text, responser = resp)
            time.sleep(duration - 2 + 1)


if __name__ == '__main__':
    shutil.rmtree(f'{fc.AUDIO_PATH}/temp', ignore_errors = True)
    utils.initialize_vars()
    SpeechService().start()
    utils.GLOBAL_LOGGER.info('SpeechService is started.')