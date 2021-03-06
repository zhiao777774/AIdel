import cv2
import base64
import numpy as np
from PIL import Image
from io import BytesIO
# from imutils import perspective #imutils在pi上有出錯，記得修正
# from skimage.filters import threshold_local


class NPImage:
    def __init__(self, frame):
        self._frame = frame.copy()
        self._original = frame.copy()

    def cvt_rgb(self):
        self._frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        
    def cvt_gray(self):
        self._frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
    
    def threshold(self):
        _, binary = cv2.threshold(self.frame, 127, 255, cv2.THRESH_BINARY)
        self._frame = binary
    
    def morphologyEx(self, mode = cv2.MORPH_OPEN, kernel = None):
        if mode not in (cv2.MORPH_OPEN, cv2.MORPH_CLOSE):
            raise BaseException('type only can be MORPH_OPEN or MORPH_CLOSE')

        kernel = kernel or np.ones((3, 3), np.uint8)
        self._frame = cv2.morphologyEx(self.frame, mode, kernel)
        
    def dilate(self, nIter = 1, kernel = None):
        kernel = kernel or np.ones((3, 3), np.uint8)
        self._frame = cv2.dilate(self.frame, kernel, iterations = nIter)
        
    def erode(self, nIter = 1, kernel = None):
        kernel = kernel or np.ones((3, 3), np.uint8)
        self._frame = cv2.erode(self.frame, kernel, iterations = nIter)

    def blur(self):
        self._frame = cv2.GaussianBlur(self.frame, (11, 11), 0)

    def canny(self, lower, upper, edges = None):
        self._frame = cv2.Canny(self.frame, lower, upper, edges)

    def find_contours(self):
        self.cvt_gray()
        self.threshold()
        self.erode()
        # self.blur()
        # self.canny(lower = 30, upper = 150)

        _, contours, _ = cv2.findContours(self.frame, 
            cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        return contours
    '''
    def cvt_to_overlook(self, original_frame):
        h, w, _ = original_frame.shape
        screenCnt = np.array([
            [0, h], #左下
            [int(w / 4), int(h / 2)], #左上
            [w, h], #右下
            [w - int(w / 4), int(h / 2)] #右上
        ], 'float32')
        warped = perspective.four_point_transform(original_frame, screenCnt.reshape(4, 2))
        #warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)  
        #T = threshold_local(warped, 11, offset = 10, method = 'gaussian')
        #warped = (warped > T).astype('uint8') * 255

        return warped
    
    def _draw_lines(self, original_frame, lines, color = [255, 0, 0], thickness = 3):
        if lines is None:
            return

        frame = np.copy(original_frame)

        try:
            print(frame.shape)
            h, w = frame.shape
            channels = frame.shape[2]
        except IndexError:
            channels = 1
        except ValueError:
            h, w, channels = frame.shape
        
        new_frame = np.zeros((h, w, channels), dtype = np.uint8)

        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(new_frame, (x1, y1), (x2, y2), color, thickness)

        frame = cv2.addWeighted(frame, 0.8, new_frame, 1.0, 0.0)
        return frame
    '''
    @property
    def frame(self):
        return self._frame

    @property
    def original(self):
        return self._original


def np_cvt_base64img(np_image, _format='JPEG'):
    buffered = BytesIO()
    img = Image.fromarray(np_image)
    img.save(buffered, format=_format)

    buffered.seek(0)
    base64img_str = base64.b64encode(buffered.getvalue()).decode()
    return base64img_str