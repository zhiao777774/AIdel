import googletrans
import translate as pytrans


def google_translate(phrase, target = 'zh-TW'):
    translator = googletrans.Translator()
    translation = translator.translate(phrase, dest = target)

    return translation.text

def translate(phrase, source, target):
    translator = pytrans.Translator(from_lang = source, to_lang = target)
    return translator.translate(phrase)