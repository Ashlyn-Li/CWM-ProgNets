# -*- coding: utf-8 -*-
"""
Created on Mon May 22 20:21:34 2023

@author: Ashlyn
"""

import numpy as np

t = np.loadtxt('interval_0.0001.txt')

data = t[:,1]

print(np.mean(data))
print(min(data))
print(max(data))