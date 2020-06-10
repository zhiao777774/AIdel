# -*- coding: utf-8 -*-
"""
Class definition of YOLO_v3 style detection model on image and video
"""

import colorsys
import os
from timeit import default_timer as timer

import numpy as np
from keras import backend as K
from keras.models import load_model
from keras.layers import Input
from PIL import Image, ImageFont, ImageDraw

from yolo3.model import yolo_eval, yolo_body, tiny_yolo_body
from yolo3.utils import letterbox_image
import os
from keras.utils import multi_gpu_model

class YOLO(object):
    _defaults = {
        "model_path": 'model_data/yolo.h5',
        "anchors_path": 'model_data/yolo_anchors.txt',
        "classes_path": 'model_data/coco_classes.txt',
        "score" : 0.3,
        "iou" : 0.45,
        "model_image_size" : (416, 416),
        "gpu_num" : 1,
    }

    @classmethod
    def get_defaults(cls, n):
        if n in cls._defaults:
            return cls._defaults[n]
        else:
            return "Unrecognized attribute name '" + n + "'"

    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults) # set up default values
        self.__dict__.update(kwargs) # and update with user overrides
        self.class_names = self._get_class()
        self.anchors = self._get_anchors()
        self.sess = K.get_session()
        self.boxes, self.scores, self.classes = self.generate()

    def _get_class(self):
        classes_path = os.path.expanduser(self.classes_path)
        with open(classes_path) as f:
            class_names = f.readlines()
        class_names = [c.strip() for c in class_names]
        return class_names

    def _get_anchors(self):
        anchors_path = os.path.expanduser(self.anchors_path)
        with open(anchors_path) as f:
            anchors = f.readline()
        anchors = [float(x) for x in anchors.split(',')]
        return np.array(anchors).reshape(-1, 2)

    def generate(self):
        model_path = os.path.expanduser(self.model_path)
        assert model_path.endswith('.h5'), 'Keras model or weights must be a .h5 file.'

        # Load model, or construct model and load weights.
        num_anchors = len(self.anchors)
        num_classes = len(self.class_names)
        is_tiny_version = num_anchors==6 # default setting
        try:
            self.yolo_model = load_model(model_path, compile=False)
        except:
            self.yolo_model = tiny_yolo_body(Input(shape=(None,None,3)), num_anchors//2, num_classes) \
                if is_tiny_version else yolo_body(Input(shape=(None,None,3)), num_anchors//3, num_classes)
            self.yolo_model.load_weights(self.model_path) # make sure model, anchors and classes match
        else:
            assert self.yolo_model.layers[-1].output_shape[-1] == \
                num_anchors/len(self.yolo_model.output) * (num_classes + 5), \
                'Mismatch between model and given anchor and class sizes'

        print('{} model, anchors, and classes loaded.'.format(model_path))

        # Generate colors for drawing bounding boxes.
        hsv_tuples = [(x / len(self.class_names), 1., 1.)
                      for x in range(len(self.class_names))]
        self.colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
        self.colors = list(
            map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)),
                self.colors))
        np.random.seed(10101)  # Fixed seed for consistent colors across runs.
        np.random.shuffle(self.colors)  # Shuffle colors to decorrelate adjacent classes.
        np.random.seed(None)  # Reset seed to default.

        # Generate output tensor targets for filtered bounding boxes.
        self.input_image_shape = K.placeholder(shape=(2, ))
        if self.gpu_num>=2:
            self.yolo_model = multi_gpu_model(self.yolo_model, gpus=self.gpu_num)
        boxes, scores, classes = yolo_eval(self.yolo_model.output, self.anchors,
                len(self.class_names), self.input_image_shape,
                score_threshold=self.score, iou_threshold=self.iou)
        return boxes, scores, classes

    def detect_image(self, image):
        start = timer()

        if self.model_image_size != (None, None):
            assert self.model_image_size[0]%32 == 0, 'Multiples of 32 required'
            assert self.model_image_size[1]%32 == 0, 'Multiples of 32 required'
            boxed_image = letterbox_image(image, tuple(reversed(self.model_image_size)))
        else:
            new_image_size = (image.width - (image.width % 32),
                              image.height - (image.height % 32))
            boxed_image = letterbox_image(image, new_image_size)
        image_data = np.array(boxed_image, dtype='float32')

        print(image_data.shape)
        image_data /= 255.
        image_data = np.expand_dims(image_data, 0)  # Add batch dimension.

        out_boxes, out_scores, out_classes = self.sess.run(
            [self.boxes, self.scores, self.classes],
            feed_dict={
                self.yolo_model.input: image_data,
                self.input_image_shape: [image.size[1], image.size[0]],
                K.learning_phase(): 0
            })

        print('Found {} boxes for {}'.format(len(out_boxes), 'img'))

        font = ImageFont.truetype(font='font/FiraMono-Medium.otf',
                    size=np.floor(3e-2 * image.size[1] + 0.5).astype('int32'))
        thickness = (image.size[0] + image.size[1]) // 300

        objs = []
        for i, c in reversed(list(enumerate(out_classes))):
            predicted_class = self.class_names[c]
            box = out_boxes[i]
            score = out_scores[i]

            label = '{} {:.2f}'.format(predicted_class, score)
            draw = ImageDraw.Draw(image)
            label_size = draw.textsize(label, font)

            top, left, bottom, right = box
            top = max(0, np.floor(top + 0.5).astype('int32'))
            left = max(0, np.floor(left + 0.5).astype('int32'))
            bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
            right = min(image.size[0], np.floor(right + 0.5).astype('int32'))
            objs.append((predicted_class, score, (left, top, right, bottom)))
            print(label, (left, top), (right, bottom))

            if top - label_size[1] >= 0:
                text_origin = np.array([left, top - label_size[1]])
            else:
                text_origin = np.array([left, top + 1])

            # My kingdom for a good redistributable image drawing library.
            for i in range(thickness):
                draw.rectangle(
                    [left + i, top + i, right - i, bottom - i],
                    outline=self.colors[c])
            draw.rectangle(
                [tuple(text_origin), tuple(text_origin + label_size)],
                fill=self.colors[c])
            draw.text(text_origin, label, fill=(0, 0, 0), font=font)
            del draw

        end = timer()
        print(end - start)
        return image, objs

    def close_session(self):
        self.sess.close()

def detect_video(yolo, video_path, output_path = ''):
    import cv2

    vid = cv2.VideoCapture(video_path)
    if not vid.isOpened():
        raise IOError("Couldn't open webcam or video")
    video_FourCC = int(vid.get(cv2.CAP_PROP_FOURCC))
    video_fps = vid.get(cv2.CAP_PROP_FPS)
    video_size = (int(vid.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    isOutput = True if output_path != "" else False
    if isOutput:
        print('!!! TYPE:', type(output_path), type(video_FourCC), type(video_fps), type(video_size))
        out = cv2.VideoWriter(output_path, video_FourCC, video_fps, video_size)
    accum_time = 0
    curr_fps = 0
    fps = 'FPS: ??'
    prev_time = timer()
    while True:
        return_value, frame = vid.read()
        image = Image.fromarray(frame)
        image, objs = yolo.detect_image(image)
        result = np.asarray(image)
        curr_time = timer()
        exec_time = curr_time - prev_time
        prev_time = curr_time
        accum_time = accum_time + exec_time
        curr_fps = curr_fps + 1
        if accum_time > 1:
            accum_time = accum_time - 1
            fps = f'FPS: {curr_fps}'
            curr_fps = 0
        cv2.putText(result, text = fps, org = (3, 15), fontFace = cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale = 0.50, color = (255, 0, 0), thickness = 2)
        cv2.namedWindow('result', cv2.WINDOW_NORMAL)
        cv2.imshow('result', result)
        if isOutput:
            out.write(result)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    yolo.close_session()

def detect_image(yolo, image_path):
    try:
        image = Image.open(image_path)
    except:
        print('Open Error! Try again!')
    else:
        image, objs = yolo.detect_image(image)
        image.show()
    yolo.close_session()

def detect_realtime(yolo, output_path = ''):
    import cv2
    import numpy as np
    import math
    import queue
    from enum import Enum
    from collections import namedtuple
    import os
    import json

    ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

    def write_json(path, data):
        path = path if ROOT_PATH in path else (ROOT_PATH + '/' + path)

        with open(path , 'w') as writer:
            data = json.dumps(data)
            writer.write(data)
            return True

        return False

    def _create_environmental_model(bboxes):
        _to_str = lambda dic: dict(zip(
                map(lambda k: k, dic.keys()),
                map(lambda v: str(v), dic.values())
            ))

        json = []
        for bbox in bboxes:
            lt = _to_str(dict(bbox.coordinates.lt._asdict()))
            rt = _to_str(dict(bbox.coordinates.rt._asdict()))
            lb = _to_str(dict(bbox.coordinates.lb._asdict()))
            rb = _to_str(dict(bbox.coordinates.rb._asdict()))

            json.append({
                'class': bbox.clsName,
                'confidence': str(bbox.confidence),
                'distance': str(bbox.distance),
                'coordinate': {
                    'lt': lt,
                    'rt': rt,
                    'lb': lb,
                    'rb': rb,
                }
            })

        write_json('model_data/environmentalModel.json', json)

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

        @property
        def distance(self):
            return self._distance if self._distance else None

        @distance.setter
        def distance(self, distance):
            self._distance = distance

    class Measurementor:
        def __init__(self, focal_length):
            self._focal_length = focal_length
        
        def measure(self, acutal_size, rad):
            distance = (self._focal_length * acutal_size) / rad
            return distance

    class StrEnum(str, Enum):
        pass

    class MazeSymbol(StrEnum):
        START = 'O'
        END = 'X'
        OBSTACLE = '#'
        ROAD = ' '
        PATH = '+ '

        def __str__(self):
            return self.value

        def __repr__(self):
            return self.value

    class Dodger:
        def __init__(self, maze):
            self._seq = queue.Queue()
            self._seq.put('')
            self._maze = maze
            self._directions = ''

        def calculate(self):
            s = ''
            while not self._end(s):
                s = self.seq.get()
                for direction in ('L', 'R', 'U', 'D'):
                    data = s + direction
                    if self._validate(data):
                        self.seq.put(data)

        def _end(self, directions):
            maze = self.maze
            start = 0

            for i, symbol in enumerate(maze[-1]):
                if symbol == MazeSymbol.START:
                    start = i
                    break

            x = start
            y = len(maze) - 1
            for direction in directions:
                if direction == 'L':
                    x -= 1
                elif direction == 'R':
                    x += 1
                elif direction == 'U':
                    y -= 1
                elif direction == 'D':
                    y += 1

            if maze[y][x] == MazeSymbol.END:
                print('Found: ' + directions)
                self._directions = directions
                return True
            return False

        def _validate(self, directions):
            maze = self.maze
            start = 0

            for i, symbol in enumerate(maze[-1]):
                if symbol == MazeSymbol.START:
                    start = i
                    break

            x = start
            y = len(maze) - 1
            for direction in directions:
                if direction == 'L':
                    x -= 1
                elif direction == 'R':
                    x += 1
                elif direction == 'U':
                    y -= 1
                elif direction == 'D':
                    y += 1

                if not (0 <= x < len(maze[0]) and 0 <= y < len(maze)):
                    return False
                elif maze[y][x] == MazeSymbol.OBSTACLE:
                    return False

            return True

        def print_maze(self):
            maze = self.maze
            start = 0

            for i, symbol in enumerate(maze[-1]):
                if symbol == MazeSymbol.START:
                    start = i
                    break

            x = start
            y = len(maze) - 1
            sequence = set()
            for direction in self.directions:
                if direction == 'L':
                    x -= 1
                elif direction == 'R':
                    x += 1
                elif direction == 'U':
                    y -= 1
                elif direction == 'D':
                    y += 1
                sequence.add((y, x))

            for y, row in enumerate(maze):
                for x, col in enumerate(row):
                    if (y, x) in sequence:
                        print(MazeSymbol.PATH, end = '')
                    else:
                        print(col + ' ', end = '')
                print()

        @property
        def seq(self):
            return self._seq

        @property
        def maze(self):
            return self._maze

        @property
        def directions(self):
            return self._directions

    def generate_maze(data, width, height, resolution, benchmark = 0):
        if width % resolution != 0 or height % resolution != 0:
            print(f'height: {height}, width: {width}')
            raise ArithmeticError('resolution should be divisible by width and height.')

        #sorting the data by distance (Ascending)
        data.sort(key = lambda bbox: bbox.distance)

        maze = []
        row_len = int(height / resolution) + 1
        row_len += 1 #adding default row (for end)
        row_len += 1 #adding default row (for user)
        col_len = int(width / resolution) + 1

        if col_len % 2 != 0: col_len -= 1

        #generating empty maze
        for i in range(row_len):
            maze.append([])
            for j in range(col_len):
                maze[i].append(MazeSymbol.ROAD)

        #setting start
        maze[row_len - 1][int((col_len - 1) / 2)] = MazeSymbol.START

        #setting end
        maze[0][int((col_len - 1) / 2)] = MazeSymbol.END

        #setting obstacles
        for bbox in data:
            lb = bbox.coordinates.lb
            rb = bbox.coordinates.rb

            y = math.ceil((lb.y - benchmark + resolution) / resolution)
            for x in range(lb.x, rb.x + resolution, resolution):
                x = math.ceil(x / resolution)
                if x >= col_len: x -= 1

                maze[y][x] = MazeSymbol.OBSTACLE

        return maze

    capture = cv2.VideoCapture(0)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 630)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

    video_FourCC = cv2.VideoWriter_fourcc(*'XVID')
    video_fps = 100.0
    video_size = (630, 360)
    
    isOutput = True if output_path != '' else False
    if isOutput:
        print('!!! TYPE:', type(output_path), type(video_FourCC), type(video_fps), type(video_size))
        out = cv2.VideoWriter(output_path, video_FourCC, video_fps, video_size)

    accum_time = 0
    curr_fps = 0
    fps = 'FPS: ??'
    prev_time = timer()
    while True:
        frame = capture.read()[1]
        frame = cv2.resize(frame, (630, 360))
        image = Image.fromarray(frame)
        image, objs = yolo.detect_image(image)
        result = np.asarray(image)

        bboxes = []
        if objs:
            h = result.shape[0]
            w = result.shape[1]

            bboxes = [BoundingBox(det) for det in objs]
            bboxes = [bbox for bbox in bboxes 
                if bbox.coordinates.lb.y >= int(h / 2)]
            bboxes = [bbox for bbox in bboxes
                if bbox.width * bbox.height >= int((h / 4) * (w / 4))]

            for bbox in bboxes:
                rad = bbox.width
                size = bbox.minEnclosingCircle()
                calibration_distance = 30
                focallen = 14.092526690391459 #物距30公分下的相機焦距
                measurementor = Measurementor(focallen)
                distance = measurementor.measure(size, rad)

                if distance < calibration_distance:
                    distance += calibration_distance
                distance = round(distance, 2)
                print(f'Distance in cm {distance}')

                bbox.distance = distance
                x = int(bbox.center()[0] - bbox.width / 4)
                y = int(bbox.coordinates.lt.y - 10)
                cv2.putText(result, text = f'{distance}cm', org = (x, y), 
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX, fontScale = 0.50, 
                    color = (0, 0, 255), thickness = 2)

            _create_environmental_model(bboxes)

        if bboxes: 
            h = int(result.shape[0] / 2)
            w = result.shape[1]
            
            maze = generate_maze(data = bboxes, height = h, width = w, benchmark = h, resolution = 90)
            dodger = Dodger(maze)
            dodger.calculate()
            dodger.print_maze()
            dirs = dodger.directions

            #time.sleep(1) #delay 1s

        curr_time = timer()
        exec_time = curr_time - prev_time
        prev_time = curr_time
        accum_time = accum_time + exec_time
        curr_fps = curr_fps + 1
        if accum_time > 1:
            accum_time = accum_time - 1
            fps = f'FPS: {curr_fps}'
            curr_fps = 0

        cv2.putText(result, text = fps, org = (3, 15), fontFace = cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale = 0.50, color = (255, 0, 0), thickness = 2)
        cv2.namedWindow('result', cv2.WINDOW_NORMAL)
        cv2.imshow('result', result)
        if isOutput:
            out.write(result)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    yolo.close_session()

def detect(yolo, frame):
    image = Image.fromarray(frame)
    image, objs = yolo.detect_image(image)
    result = np.asarray(image)

    return result, objs

if __name__ == '__main__':
    yolo = YOLO(anchors_path = 'model_data/tiny_yolo_anchors.txt')
    detect_realtime(yolo)