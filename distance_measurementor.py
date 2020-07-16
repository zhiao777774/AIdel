class Measurementor:
    def __init__(self, focal_length):
        self._focal_length = focal_length
        
    def measure(self, acutal_size, rad):
        distance = (self._focal_length * acutal_size) / rad
        return distance

class Calibrationor:
    def __init__(self, distance):
        self._distance_to_object = distance
        
    def calibration(self, acutal_size, rad):
        focallen = (self._distance_to_object * rad) / acutal_size
        return focallen


if __name__ == '__main__':
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

    def _calibrate(calibration_distance, bbox):
        rad = bbox.width
        size = bbox.minEnclosingCircle()
        print(f"min enclosing circle's radius: {size}")
        focallen = Calibrationor(calibration_distance).calibration(size, rad)
        print(f'Focal lenght is {focallen} Pixels')

        return focallen

    def _measure(calibration_distance, focallen, bbox):
        rad = bbox.width
        size = bbox.minEnclosingCircle()
        print(f"min enclosing circle's radius: {size}")
        measurementor = Measurementor(focallen)
        distance = measurementor.measure(size, rad)

        if distance < calibration_distance:
            distance += calibration_distance
        print(f'Distance in cm {distance}')

        return distance


    calibration_distance = 35 #校準時的距離
    bbox = BoundingBox(('bottle', 0.84, (255, 72, 385, 356))) #35cm
    focallen = _calibrate(calibration_distance, bbox)  #物距35公分下的相機焦距

    focallen = 14.536741214057509 #物距35公分下的相機焦距
    #bbox = BoundingBox(('cell phone', 0.55, (159, 110, 291, 357))) #30cm時
    bbox = BoundingBox(('person', 0.65, (87, 49, 555, 344))) #45cm時
    distance = _measure(calibration_distance, focallen, bbox)