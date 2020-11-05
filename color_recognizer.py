import cv2
import numpy as np
import pandas as pd

from .file_controller import ROOT_PATH


index = ['color', 'color_name', 'hex', 'R', 'G', 'B']
_COLOR_MAPPER = pd.read_csv(f'{ROOT_PATH}/data/colors.csv', names = index, header = None)

def getColorName(R, G, B):
    minimum = 10000
    for i in range(len(_COLOR_MAPPER)):
        d = abs(R - int(_COLOR_MAPPER.loc[i, 'R'])) + \
            abs(G - int(_COLOR_MAPPER.loc[i, 'G'])) + \
            abs(B - int(_COLOR_MAPPER.loc[i, 'B']))

        if(d <= minimum):
            minimum = d
            cname = _COLOR_MAPPER.loc[i, 'color_name']

    return cname

def color_recognize(frame, y, x):
    b, g, r = frame[y, x]
    b = int(b)
    g = int(g)
    r = int(r)

    return getColorName(r, g, b), r, g, b

def is_rgb(frame, y, x, target):
    b, g, r = frame[y, x]
    b = int(b)
    g = int(g)
    r = int(r)

    if target == 'r': 
        target = r
        another = g, b
    elif target == 'g':
        target = g
        another = r, b
    elif target == 'b':
        target = b
        another = r, g
    else:
        raise TypeError('target must be r, g, or b.')

    return target >= another[0] and target >= another[1]