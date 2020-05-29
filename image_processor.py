import cv2
import numpy as np
from imutils import perspective
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

    def cvt_to_overlook(self, original_frame):
        h, w, _ = original_frame.shape
        screenCnt = np.array([
            [1, h - 1],
            [int(w / 4), int(h / 2)],
            [w - 1, h - 1],
            [w - int(w / 4), int(h / 2)]
        ], 'float32')
        warped, m = self.corners_unwarp(original_frame)
        #warped = perspective.four_point_transform(original_frame, screenCnt.reshape(4, 2))
        #warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)  
        #T = threshold_local(warped, 11, offset = 10, method = 'gaussian')
        #warped = (warped > T).astype('uint8') * 255

        return warped

    # Define a function that takes an image, number of x and y points, 
    # camera matrix and distortion coefficients
    def corners_unwarp(self, img, nx, ny, mtx, dist):
        # Use the OpenCV undistort() function to remove distortion
        undist = cv2.undistort(img, mtx, dist, None, mtx)
        # Convert undistorted image to grayscale
        gray = cv2.cvtColor(undist, cv2.COLOR_BGR2GRAY)
        # Search for corners in the grayscaled image
        ret, corners = cv2.findChessboardCorners(gray, (nx, ny), None)

        if ret == True:
            # If we found corners, draw them! (just for fun)
            cv2.drawChessboardCorners(undist, (nx, ny), corners, ret)
            # Choose offset from image corners to plot detected corners
            # This should be chosen to present the result at the proper aspect ratio
            # My choice of 100 pixels is not exact, but close enough for our purpose here
            offset = 100 # offset for dst points
            # Grab the image shape
            img_size = (gray.shape[1], gray.shape[0])

            # For source points I'm grabbing the outer four detected corners
            src = np.float32([corners[0], corners[nx-1], corners[-1], corners[-nx]])
            # For destination points, I'm arbitrarily choosing some points to be
            # a nice fit for displaying our warped result 
            # again, not exact, but close enough for our purposes
            dst = np.float32([[offset, offset], [img_size[0]-offset, offset], 
                                         [img_size[0]-offset, img_size[1]-offset], 
                                         [offset, img_size[1]-offset]])
            # Given src and dst points, calculate the perspective transform matrix
            M = cv2.getPerspectiveTransform(src, dst)
            # Warp the image using OpenCV warpPerspective()
            warped = cv2.warpPerspective(undist, M, img_size)

            # Return the resulting image and matrix
            return warped, M

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
        line1 = lines[0][0]
        line2 = lines[0][1]

        self.poly = np.array([
            [line1[0], line1[1]],
            [line1[2], line1[3]],
            [line2[0], line2[1]],
            [line2[2], line2[3]]], 'float32')

        frame = cv2.addWeighted(frame, 0.8, new_frame, 1.0, 0.0)
        return frame

    @property
    def frame(self):
        return self._frame

if __name__ == "__main__":

    def _track():
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

    def _image_preprocess(frame):
        processor = ImageProcessor(frame)
        processor.basic_preprocess()
        return processor.frame

    def _project_to_2d(frame):
        processor = ImageProcessor(frame)
        #processor.region_of_interest()
        #return processor.frame
        return processor.cvt_to_overlook(frame)
    
    #capture = cv2.VideoCapture(0)
    #frame = capture.read()[1]
    frame = cv2.imread(r'aidel\testImage\test3.jpg')
    cv2.imshow('original' ,frame)

    #frame = _image_preprocess(frame)
    frame = _project_to_2d(frame)  
    cv2.imshow('projection' ,frame)

    cv2.waitKey(0)
    cv2.destroyAllWindows()