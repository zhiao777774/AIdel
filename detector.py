import yoloKeras.yolo as yolo

import file_controller as fc

MODEL_PATH = f'{fc.ROOT_PATH}/yoloKeras/model_data'
_model = yolo.YOLO(anchors_path = f'{MODEL_PATH}/tiny_yolo_anchors.txt')

def detect(frame):
    image, dets = yolo.detect(_model, frame)
    return image, dets


import math
from collections import namedtuple

class BoundingBox:
    def __init__(self, det):
        self._clsName, self._confidence = det[0], det[1]
        self._coordinates = self._calc_coordinates(det[2])
        
        coords = self.coordinates
        self._width = coords.rt.x - coords.lt.x
        self._height = coords.lb.y - coords.lt.y
        self._xCenter = coords.lt.x + (self.width / 2)
        self._yCenter = coords.lt.y + (self.height / 2)
        
    def _calc_coordinates(self, bounds):
        l, t, r, b = bounds
        coords_tuple = namedtuple('coords_tuple', ['lt' , 'rt', 'lb', 'rb'])
        coord_tuple = namedtuple('coord_tuple', ['x' , 'y'])
        
        lt_x, lt_y = l, t
        rt_x, rt_y = r, t
        lb_x, lb_y = l, b
        rb_x, rb_y = r, b
        
        coords = coords_tuple(coord_tuple(lt_x, lt_y),
                              coord_tuple(rt_x, rt_y),
                              coord_tuple(lb_x, lb_y),
                              coord_tuple(rb_x, rb_y))
        return coords
        
    def minEnclosingCircle(self):
        sqrt = (self.width ** 2) + (self.height ** 2)
        return int(math.ceil(sqrt ** 0.5))
    
    def center(self):
        return self.xCenter, self.yCenter
        
    @property
    def clsName(self):
        return self._clsName
    
    @property
    def confidence(self):
        return self._confidence
    
    @property
    def coordinates(self):
        return self._coordinates
    
    @property
    def xCenter(self):
        return self._xCenter
    
    @property
    def yCenter(self):
        return self._yCenter
    
    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height