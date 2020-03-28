# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 03:18:38 2020

@author: 許智豪
"""

from threading import Thread
import time
import wave, pyaudio
import speech_recognition as sr
import jieba

import file_controller as fc

class SpeechService(Thread):
    def __init__(self):
        Thread.__init__(self)
        
        dict_path = "%s/dict.txt.big.txt" % fc.ROOT_PATH
        jieba.set_dictionary(dict_path)
        
        self._triggerable_keywords = fc.read_json("triggerable_keywords.json")
        
    def run(self):
        while True:
            print('Recording...')
            sentence = self.voice2text()
            
            triggerable = len([k for k in self._triggerable_keywords if k in sentence]) > 0
            if not triggerable: continue 
        
            sentence = _replace_and_trim(sentence, "AIDEL")
            keywords = [k for k in ("尋找", "是否", "導航") if k in sentence]
        
            if ("導航" in keywords) & (len(keywords) >= 2):
                continue
        
            keyword = keywords[1 if len(keywords) >= 2 else 0]
            words = self.sentence_segment(sentence)
            
    def voice2text(self):
        audio = None
        text = None
    
        #self._record_wave()
        device = self.get_device()
        r = sr.Recognizer()
        with sr.Microphone(device_index = device["index"]) as source: 
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        """
        r = sr.Recognizer()
        with sr.AudioFile('record.wav') as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        """
        try:
            text = r.recognize_google(audio, language = "zh-TW")
        except sr.UnknownValueError:
            text = "無法翻譯"
        except sr.RequestError as e:
            text = "無法翻譯{0}".format(e)

        print(text)
        return text

    def _record_wave(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        RATE = 16000
        CHANNELS = 1
        RECORD_SECONDS = 5

        pa = pyaudio.PyAudio()
        stream = pa.open(format = FORMAT,
                         channels = CHANNELS,
                         rate = RATE,
                         input = True,
                         frames_per_buffer = CHUNK)
        print('Recording...')
        buffer = []
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            audio_data = stream.read(CHUNK, exception_on_overflow = False)
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

    def get_device(self):
        pa = pyaudio.PyAudio()
        return pa.get_default_input_device_info()
    
def _replace_and_trim(text, old, new = ""):
    return text.replace(old, new).strip()


import googlemaps

class GoogleService:
    def __init__(self):
        gmaps_key = ""
        self._gmaps = googlemaps.Client(key = gmaps_key)
        
    def positioning(self):
        return ()
    
    def places_radar(self, type_):
        radarResults = self._gmaps.places_radar(location = self.positioning(), 
                                          radius = 200, 
                                          type = type_)
        return radarResults["results"]
    
    def navigate(self):
        pass


if __name__ == "__main__":
    while True:
        audio = None
        text = None
        pa = pyaudio.PyAudio()
        device = pa.get_default_input_device_info()

        print("Recording...")
        r = sr.Recognizer()
        with sr.Microphone(device_index = device["index"]) as source: 
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        
        try:
            text = r.recognize_google(audio, language = "zh-TW")
        except sr.UnknownValueError:
            text = "無法翻譯"
        except sr.RequestError as e:
            text = "無法翻譯{0}".format(e)
        print(text)
        
        dict_path = r"D:\Anaconda\Lib\site-packages\jieba\dict.txt.big.txt"
        jieba.set_dictionary(dict_path)
    
        words = jieba.lcut(text)
        print(words)