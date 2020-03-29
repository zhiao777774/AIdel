import darknet.python.darknet as dn

import file_controller as fc

dn_path = "%s/darknet" % fc.ROOT_PATH
#配置cpu
dn.set_gpu(0)
#配置網絡文件及權重文件
_net = dn.load_net(str.encode("%s/cfg/yolov3-tiny.cfg" % dn_path),
                      str.encode("%s/weights/yolov3-tiny.weights" % dn_path), 0)
#配置數據集分類文件
_meta = dn.load_meta(str.encode("%s/cfg/coco.data" % dn_path))

def detect(frame, thresh=.5, hier_thresh=.5, nms=.45):
    """
    物體檢測函數
    
    Parameters:
        -frame : OpenCV Image(=Numpy array)
            影像數據.
        -thresh : NUMBER(0-1), optional
            機率低於此閾值的預測邊界框將被優先過濾. The default is .5.
        -hier_thresh : NUMBER(0-1), optional
            針對最大機率邊界框進行類別判斷時的閾值. The default is .5.
        -nms : NUMBER(0-1), optional
            非最大值抑制處理時的閾值. The default is .45.

    Returns:
        -dets : LIST(=>[物體1, 物體2, 物體3, ...])
            物體檢測結果.
            物體 : TUPLE(=>(分類名稱, 分類自信度, (物體中心x, 物體中心y, 物體寬度, 物體高度)))
    """
    dets = dn.detect_np(_net, _meta. frame, thresh, hier_thresh, nms)
    return dets


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
        
        coords_tuple = namedtuple("coords_tuple", ["lt" , "rt", "lb", "rb"])
        coord_tuple = namedtuple("coord_tuple", ["x" , "y"])
        
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