# -*- coding: utf-8 -*-
"""
Created on Sat Jan 18 03:41:37 2020

@author: 許智豪
"""

import os, sys

if not __package__:
  path = os.path.join(os.path.dirname(__file__), os.pardir)
  sys.path.insert(0, path)
  
import aidel
aidel.initialize()