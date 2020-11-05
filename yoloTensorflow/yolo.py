import os
import numpy as np
import cv2
import tensorflow as tf
import platform
from PIL import Image

import core.utils as utils
from core.yolov4 import filter_boxes


physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
EDGETPU_SHARED_LIB = {
    'Linux': 'libedgetpu.so.1',
    'Darwin': 'libedgetpu.1.dylib',
    'Windows': 'edgetpu.dll'
}[platform.system()]

class YOLO:
    _defaults = {
        'model_path': f'{ROOT_PATH}/data/yolov4-416.tflite',
        'framework': 'tflite',
        'tiny': False,
        'model': 'yolov4',
        'score': 0.3,
        'iou': 0.45,
        'model_image_size': (416, 416)
    }

    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults)  # set up default values
        self.__dict__.update(kwargs)  # and update with user overrides

        interpreter = tf.lite.Interpreter(
            model_path=self.model_path,
            experimental_delegates=[
                tf.lite.experimental.load_delegate(EDGETPU_SHARED_LIB)])

        interpreter.allocate_tensors()
        self.input_details = interpreter.get_input_details()
        self.output_details = interpreter.get_output_details()
        print(self.input_details)
        print(self.output_details)

        self.interpreter = interpreter

    def detect_image(self, image):
        input_size = self.model_image_size

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_data = cv2.resize(image, input_size)
        image_data = image_data / 255.
        images_data = [image_data]
        images_data = np.asarray(images_data).astype(np.float32)

        self.interpreter.set_tensor(
            self.input_details[0]['index'], images_data)
        self.interpreter.invoke()
        pred = [self.interpreter.get_tensor(self.output_details[i]['index'])
                for i in range(len(self.output_details))]
        if self.model == 'yolov3' and self.tiny == True:
            boxes, pred_conf = filter_boxes(
                pred[1], pred[0], score_threshold=0.25, input_shape=tf.constant([input_size]))
        else:
            boxes, pred_conf = filter_boxes(
                pred[0], pred[1], score_threshold=0.25, input_shape=tf.constant([input_size]))

        boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
            boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
            scores=tf.reshape(
                pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
            max_output_size_per_class=50,
            max_total_size=50,
            iou_threshold=self.iou,
            score_threshold=self.score
        )

        pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(),
                     valid_detections.numpy()]
        image, objs = utils.draw_bbox(image, pred_bbox)
        image = Image.fromarray(image.astype(np.uint8))
        image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)

        for o in objs: print(o)

        return image, objs

def detect_realtime(yolo):
    capture = cv2.VideoCapture(0)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 630)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

    while True:
        frame = capture.read()[1]
        result, dets = detect(yolo, frame)

        cv2.namedWindow('result', cv2.WINDOW_NORMAL)
        cv2.imshow('result', result)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def detect(yolo, frame):
    image, objs = yolo.detect_image(frame)
    result = np.asarray(image)

    return result, objs


if __name__ == '__main__':
    yolo = YOLO(
        model_path='data/yolov4-tiny-416.tflite', tiny=True)

    detect_realtime(yolo)