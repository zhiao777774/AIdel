import yoloKeras.yolo as yolo

import file_controller as fc

MODEL_PATH = '{}/yoloKeras/model_data' % fc.ROOT_PATH
_model = yolo.YOLO(anchors_path = '{}/tiny_yolo_anchors.txt' % MODEL_PATH)

def detect(frame):
    return yolo.detect(_model, frame) 


from collections import namedtuple

class BoundingBox:
    def __init__(self, det):
        self._clsName, self._confidence = det[0], det[1]
        self._xCenter, self._yCenter, self._width, self._height = det[2]
        
    def coordinates(self):
        x = self.xCenter
        y = self.yCenter
        w = self.width
        h = self.height
        
        coords_tuple = namedtuple('coords_tuple', ['lt' , 'rt', 'lb', 'rb'])
        coord_tuple = namedtuple('coord_tuple', ['x' , 'y'])
        
        lt_x, lt_y = (x - w / 2), (y - h / 2)
        rt_x, rt_y = (x + w / 2), (y - h / 2)
        lb_x, lb_y = (x - w / 2), (y + h / 2)
        rb_x, rb_y = (x + w / 2), (y + h / 2)
        
        coords = coords_tuple(coord_tuple(lt_x, lt_y),
                              coord_tuple(rt_x, rt_y),
                              coord_tuple(lb_x, lb_y),
                              coord_tuple(rb_x, rb_y))
        return coords
        
    def center(self):
        return self.xCenter, self.yCenter
        
    @property
    def clsName(self):
        return self._clsName
    
    @property
    def confidence(self):
        return self._confidence
    
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