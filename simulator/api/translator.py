import translate as pytrans
from google_trans_new import google_translator 


def google_translate(phrase, target = 'zh-TW'):
    translator = google_translator()
    translation = translator.translate(phrase, lang_tgt = target)

    return translation

def translate(phrase, source, target):
    translator = pytrans.Translator(from_lang = source, to_lang = target)
    return translator.translate(phrase)