import googletrans
from translate import translator


def translate(phrase, target = 'zh-TW'):
    translator = googletrans.Translator()
    translation = translator.translate(phrase, dest = target)

    return translation.text

def translate_web(source, target, phrase):
    translation = translator(
        source = source, 
        target = target, 
        phrase = phrase)

    return translation

def detect_lang(phrase):
    result = translator.detect(phrase)
    return result.lang