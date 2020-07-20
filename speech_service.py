import abc
import os
import time
import requests
import wave
import pyaudio
import speech_recognition as sr
import jieba
import jieba.analyse
from pygame import mixer
from threading import Thread
from xml.etree import ElementTree
from enum import Enum

#import word_vector_machine as wvm
import file_controller as fc


class AbstractService:
    @abc.abstractmethod
    def execute(self):
        return NotImplemented


class ServiceType(Enum):
    SEARCH = '尋找'
    WHETHER = '是否'
    NAVIGATION = '導航'

    @classmethod
    def get_service(cls, service):
        return {
            cls.SEARCH.value: '',  # GoogleService(),
            cls.WHETHER.value: '',  # GoogleService(),
            cls.NAVIGATION.value: ''  # GoogleService()
        }.get(service)


class SpeechService(Thread):
    def __init__(self):
        Thread.__init__(self)

        dict_path = f'{fc.ROOT_PATH}/data/dict.txt.big.txt'
        jieba.set_dictionary(dict_path)

        keywords_path = f'{fc.ROOT_PATH}/data/triggerable_keywords.json'
        self._triggerable_keywords = fc.read_json(keywords_path)

    def run(self):
        while True:
            print('Recording...')
            sentence = self.voice2text()

            keywords = [k for k in self._triggerable_keywords if k in sentence]
            triggerable = len(keywords) > 0
            if not triggerable:
                continue

            for k in keywords:
                sentence = _replace_and_trim(sentence, k)
            keywords = [k for k in ServiceType if k.value in sentence]

            if not keywords:
                # 同義詞搜尋
                continue
            elif (ServiceType.NAVIGATION in keywords) & (len(keywords) >= 2):
                continue

            service = keywords[1 if len(keywords) >= 2 else 0]
            words = self.sentence_segment(sentence)
            keywords = self.extract_keywords(words)

            for tag, weight in keywords:
                print(tag + ' , ' + str(weight))

            keywords = self.filter_keywords(keywords)
            service, place = self.finds(keywords, service.value)

            # ServiceType.get_service(service).execute(place)

    def voice2text(self):
        audio = None
        text = None

        # self._record_wave()
        device = self.get_device()
        r = sr.Recognizer()
        with sr.Microphone(device_index=device['index']) as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        '''
        r = sr.Recognizer()
        with sr.AudioFile('record.wav') as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        '''
        try:
            text = r.recognize_google(audio, language='zh-TW')
        except sr.UnknownValueError:
            text = '無法翻譯'
        except sr.RequestError as e:
            text = f'無法翻譯{e}'

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

    def finds(self, keywords, keyword):
        if type(keywords[0]) is tuple:
            keywords = map(lambda k: k[0], keywords)

        index = keywords.index(keyword)
        place = None

        if len(keywords) == 2:
            place = keywords[0 if index else 1]
        else:
            place = keywords[index + 1]

        return (keyword, place)

    def get_device(self):
        pa = pyaudio.PyAudio()
        return pa.get_default_input_device_info()


def _replace_and_trim(text, old, new=''):
    return text.replace(old, new).strip()


class TextToSpeech:
    def __init__(self, subscription_key, input_text):
        self.subscription_key = subscription_key
        self.tts = input_text
        self.timestr = time.strftime('%Y%m%d-%H%M')
        self.access_token = self._get_token()

    def _get_token(self):
        fetch_token_url = 'https://westus.api.cognitive.microsoft.com/sts/v1.0/issueToken'
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        return str(response.text)

    def save_audio(self):
        base_url = 'https://westus.tts.speech.microsoft.com/'
        path = 'cognitiveservices/v1'
        constructed_url = base_url + path
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': 'YOUR_RESOURCE_NAME'
        }
        xml_body = ElementTree.Element('speak', version='1.0')
        xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-us')
        voice = ElementTree.SubElement(xml_body, 'voice')
        voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-US')
        voice.set(
            'name', 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24kRUS)')
        voice.text = self.tts
        body = ElementTree.tostring(xml_body)

        response = requests.post(constructed_url, headers=headers, data=body)
        if response.status_code == 200:
            # with open('sample-' + self.timestr + '.wav', 'wb') as audio:
            with open(self.tts + '.wav', 'wb') as audio:
                audio.write(response.content)
                print('\nStatus code: ' + str(response.status_code) +
                      '\nYour TTS is ready for playback.\n')
        else:
            print('\nStatus code: ' + str(response.status_code) +
                  '\nSomething went wrong. Check your subscription key and headers.\n')


class Responser:
    def __init__(self):
        self._response = fc.read_json(f'{fc.ROOT_PATH}/data/response.json')

    def decide_response(self, direction):
        res = self._response
        return res[direction]

    def tts(self, input_text):
        subscription_key = ''
        app = TextToSpeech(subscription_key, input_text)
        app.save_audio()

    def play_audio(self, audio_name):
        mixer.init()
        mixer.music.load(f'{fc.ROOT_PATH}/data/audio/{audio_name}')
        mixer.music.play()
        while mixer.music.get_busy(): continue


'''
import googlemaps

class GoogleService(AbstractService):
    def __init__(self):
        gmaps_key = ''
        self._gmaps = googlemaps.Client(key = gmaps_key)
        
    def positioning(self):
        return ()
    
    def places_radar(self, type_):
        radarResults = self._gmaps.places_radar(location = self.positioning(), 
                                          radius = 200, 
                                          type = type_)
        return radarResults['results']
    
    def navigate(self):
        pass

    def execute(self):
        pass
'''

if __name__ == '__main__':
    while True:
        audio = None
        text = None
        pa = pyaudio.PyAudio()
        device = pa.get_default_input_device_info()

        print('Recording...')
        r = sr.Recognizer()
        with sr.Microphone(device_index = device['index']) as source: 
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        
        try:
            text = r.recognize_google(audio, language = 'zh-TW')
        except sr.UnknownValueError:
            text = '無法翻譯'
        except sr.RequestError as e:
            text = f'無法翻譯{e}'
        print(text)

        dict_path = r'D:\Anaconda\Lib\site-packages\jieba\dict.txt.big.txt'
        jieba.set_dictionary(dict_path)
    
        words = jieba.lcut(text)
        print(words)

        keywords = []
        for word in words:
            tags = jieba.analyse.extract_tags(word, topK = 5, withWeight = True)
            if tags: keywords.append(tags[0])

        for tag, weight in keywords:
            print(tag + ' , ' + str(weight))

        keywords = [k for k in keywords if k[1] >= 10]
        print(keywords)