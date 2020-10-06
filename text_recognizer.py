from pytesseract import Output
import pytesseract

from .image_processor import NPImage


TESSERACT_EXE_PATH = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE_PATH

def text_recognize(frame, target = 'chi_tra+eng', min_conf = None):
    image = NPImage(frame)
    image.cvt_rgb()

    if isinstance(target, list):
        target = '+'.join(target)

    if not min_conf:
        result = pytesseract.image_to_string(image.frame, 
            lang = target, config = '--psm 3')
        return result.split('\n')
    elif isinstance(min_conf, (int, float)):
        data = pytesseract.image_to_data(image.frame, 
            lang = target, config = '--psm 3', output_type = Output.DICT)

        for i in range(len(data['text'])):
            text = data['text'][i]
            conf = int(data['conf'][i])

            if conf >= min_conf: result.append(text)
            
        return result

    return None