import cv2
import pytesseract
from pytesseract import Output

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

def digit_recognize(frame):
    image = NPImage(frame.copy())
    image.cvt_rgb()
    image.blur()
    image.threshold()
    image.dilate(nIter = 5)
    image.erode(nIter = 5)
    image.cvt_gray()
    gray = image.frame.copy()
    image.canny(lower = 50, upper = 200, edges = 255)

    cnts = []
    contours, _ = cv2.findContours(image.frame, 
        cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
	    area = cv2.contourArea(cnt)
	    if 500 <= area <= 5000: cnts.append(cnt)

    DIGITS_LOOKUP = {
	    (1, 1, 1, 0, 1, 1, 1): 0,
	    (0, 0, 1, 0, 0, 1, 0): 1,
	    (1, 0, 1, 1, 1, 1, 0): 2,
	    (1, 0, 1, 1, 0, 1, 1): 3,
	    (0, 1, 1, 1, 0, 1, 0): 4,
	    (1, 1, 0, 1, 0, 1, 1): 5,
	    (1, 1, 0, 1, 1, 1, 1): 6,
	    (1, 0, 1, 0, 0, 1, 0): 7,
	    (1, 1, 1, 1, 1, 1, 1): 8,
	    (1, 1, 1, 1, 0, 1, 1): 9
    }

    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

    digits = []
    # loop over each of the digits
    for i, c in enumerate(cnts):
    	# extract the digit ROI
    	(x, y, w, h) = cv2.boundingRect(c)
    	roi = thresh[y:y + h, x:x + w]
    	kernel = np.ones((3, 3), np.uint8)
    	roi = cv2.morphologyEx(roi, cv2.MORPH_OPEN, kernel)
    	roi = cv2.dilate(roi, np.ones((3, 3), np.uint8), iterations = 1)

    	# compute the width and height of each of the 7 segments
    	# we are going to examine
    	(roiH, roiW) = roi.shape
    	(dW, dH) = (int(roiW * 0.25), int(roiH * 0.15))
    	dHC = int(roiH * 0.05)
    	# define the set of 7 segments
    	segments = [
    		((0, 0), (w, dH)),	# top
    		((0, 0), (dW, h // 2)),	# top-left
    		((w - dW, 0), (w, h // 2)),	# top-right
    		((0, (h // 2) - dHC) , (w, (h // 2) + dHC)), # center
    		((0, h // 2), (dW, h)),	# bottom-left
    		((w - dW, h // 2), (w, h)),	# bottom-right
    		((0, h - dH), (w, h))	# bottom
    	]
    	on = [0] * len(segments)

    	# loop over the segments
    	for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
    		# extract the segment ROI, count the total number of
    		# thresholded pixels in the segment, and then compute
    		# the area of the segment
    		segROI = roi[yA:yB, xA:xB]
    		total = cv2.countNonZero(segROI)
    		area = (xB - xA) * (yB - yA)
    		# if the total number of non-zero pixels is greater than
    		# 50% of the area, mark the segment as "on"
    		if total / float(area) > 0.5:
    			on[i]= 1
    	# lookup the digit and draw it on the image
    	try:
    		digit = DIGITS_LOOKUP[tuple(on)]
            digits.appebd(digit)
    	except KeyError:
    		continue

    return digits