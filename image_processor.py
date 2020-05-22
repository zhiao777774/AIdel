import cv2
import numpy as np

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

    def canny(self, low = 100, high = 200):
        self._frame = cv2.Canny(self.frame, low, high)

    def region_of_interest(self):
        frame = self.frame
        h, w, _ = frame.shape

        roi_vertices = [
            (0, h),
            (w / 2, h / 2),
            (w, h)
        ]

        mask = np.zeros_like(frame)
        cv2.fillPoly(mask, np.array([roi_vertices], np.int32), color = 255)
        self._frame = cv2.bitwise_and(frame, mask)

    def hough_lines(self, rho = 6, theta = (np.pi / 180), 
                threshold = 160, min_line_len = 40, max_line_gap = 25):

        lines = cv2.HoughLinesP(self.frame, rho, theta, threshold, np.array([]), 
                        min_line_len, max_line_gap)
        self._frame = lines

    def optimize_lines(self, original_frame):
        lines = self.frame
        left_x, left_y, right_x, right_y = [], [], [], []
    
        for line in lines:
            for x1, y1, x2, y2 in line:
                slope = ((y2 - y1) / (x2 - x1))
                if slope < 0:
                    left_x.extend([x1,x2])
                    left_y.extend([y1,y2])
                elif slope > 0:
                    right_x.extend([x1,x2])
                    right_y.extend([y1,y2])
    
        min_y = int(original_frame.shape[0] * (3 / 5))
        max_y = int(original_frame.shape[0])

        poly_left = np.poly1d(np.polyfit(left_y, left_x, deg = 1))
        left_x_start = int(poly_left(max_y))
        left_x_end = int(poly_left(min_y))

        poly_right = np.poly1d(np.polyfit(right_y, right_x, deg = 1))
        right_x_start = int(poly_right(max_y))
        right_x_end = int(poly_right(min_y))

        frame = self._draw_lines(original_frame, [[
                [left_x_start, max_y, left_x_end, min_y],
                [right_x_start, max_y, right_x_end, min_y]          
            ]], thickness = 5)

        self._frame = frame

    def cvt_to_overlook(self, original_frame):
        edged = self.frame
        ratio = edged.shape[0] / 500.0

        cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)  
            if len(approx) == 4:
                screenCnt = approx
                break
            
        warped = perspective.four_point_transform(original_frame, screenCnt.reshape(4, 2) * ratio)
        warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)  
        T = threshold_local(warped, 11, offset = 10, method = 'gaussian')
        warped = (warped > T).astype('uint8') * 255

        self._frame = warped

    def _draw_lines(self, original_frame, color = [255, 0, 0], thickness = 3):
        lines = self.frame

        if lines is None:
            return

        frame = np.copy(original_frame)
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