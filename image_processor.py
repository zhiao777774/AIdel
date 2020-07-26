import cv2
import numpy as np
from imutils import perspective #imutils在pi上有出錯，記得修正
from skimage.filters import threshold_local

class ImageProcessor:
    def __init__(self, frame):
        self._frame = frame
        
    def rgb2gray(self):
        self._frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
    
    def threshold(self):
        _, binary = cv2.threshold(self.frame, 127, 255, cv2.THRESH_BINARY)
        self._frame = binary
    
    def morphologyEx(self, type_ = cv2.MORPH_OPEN):
        if type_ not in (cv2.MORPH_OPEN, cv2.MORPH_CLOSE):
            raise BaseException('type only can be MORPH_OPEN or MORPH_CLOSE')

        kernel = np.ones((3, 3), np.uint8)
        self._frame = cv2.morphologyEx(self.frame, type_, kernel)
        
    def dilate(self, nIter = 1):
        self._frame = cv2.dilate(self.frame, iterations = nIter)
        
    def erode(self, nIter = 1):
        self._frame = cv2.erode(self.frame, iterations = nIter)

    def basic_preprocess(self):
        self.rgb2gray()
        self.threshold()
        self.morphologyEx()

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

    @property
    def frame(self):
        return self._frame

def track():
    # provide points from image 1
    pts_src = np.array([[154, 174], [702, 349], [702, 572],[1, 572], [1, 191]])
    # corresponding points from image 2 (i.e. (154, 174) matches (212, 80))
    pts_dst = np.array([[212, 80],[489, 80],[505, 180],[367, 235], [144,153]])
    # calculate matrix H
    h, status = cv2.findHomography(pts_src, pts_dst)
    # provide a point you wish to map from image 1 to image 2
    a = np.array([[154, 174]], dtype='float32')
    a = np.array([a])
    # finally, get the mapping
    pointsOut = cv2.perspectiveTransform(a, h)
    print(pointsOut)