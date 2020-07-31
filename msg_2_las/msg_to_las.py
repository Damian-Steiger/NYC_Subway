#!/usr/bin/env python3

import numpy as np
import msgpack
import os
import pyquanergy
b = [-0.318505, -0.2692, -0.218009, -0.165195, -0.111003, -0.0557982, 0.0, 0.0557982]

dire = os.listdir(os.getcwd())
dire.sort()


for fileName in dire:
    if fileName.endswith('.mpk'):
        with open(fileName, 'rb') as f:
            up = msgpack.Unpacker(f)
            for d in up:
                qd = pyquanergy.getQF(d[-1])
            
            
                curr_time = qd['t_secs'] + qd['t_nsecs'] / 1e9
                
                theta = np.array([2 * np.pi * (x['position'] / 10400.0) for x in qd['firings']])
                intensities = np.array([x['intensity'][-1] for x in qd['firings']])
                distances = np.array([x['distance'][-1] / 1e5 for x in qd['firings']])
                
                valid_idx = np.bitwise_and(distances > 1.3, intensities != 255)
                
                x = (np.cos(theta) * np.cos([[b[0]], [b[1]], [b[2]], [b[3]], [b[4]], [b[5]], [b[6]], [b[7]]])).T * distances
                y = (np.sin(theta) * np.cos([[b[0]], [b[1]], [b[2]], [b[3]], [b[4]], [b[5]], [b[6]], [b[7]]])).T * distances
                z = (np.cos(theta*0) * np.sin([[b[0]], [b[1]], [b[2]], [b[3]], [b[4]], [b[5]], [b[6]], [b[7]]])).T * distances
                
                points = []
                for i in range(8):
                    temp = zip(x[valid_idx[:,i], i],y[valid_idx[:,i], i],z[valid_idx[:,i], i],intensities[valid_idx[:,i], i],np.ones(z[valid_idx[:,i], i].shape)*i)
                    a = list(temp)
                    points += a
                
                
                
    
    ## this will make points a list of [x,y,z,intensity,ring #], ring number might not be required, but you will need to add time to each point.
    
