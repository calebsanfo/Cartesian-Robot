'''
eraser.py

Continually erases dots drawn on a whiteboard.

Written by Caleb Sanford (2019)
'''

import os
import sys
import random
import math
import numpy as np
import skimage.io
import matplotlib
import matplotlib.pyplot as plt
import time

sys.path.append('./mrcnn')

import utils
import model as modellib
import visualize
import config

import dot_dataset
import cam

classnames = ['BG', 'dot']

import cv2
import serial
import time

def goto(ard, x, y):
    message = str(x)+','+str(y)
    message = message.encode()
    ard.write(message)
    print(ard.readline())
    time.sleep(.5)

def erase():
    goto(ard, 'z', .2)
    goto(ard, -.25, -.25)
    goto(ard, 0, .5)
    goto(ard, .25, -.5)
    goto(ard, 0, .5)
    goto(ard, .25, -.5)
    goto(ard, 0, .5)
    goto(ard, -.25, -.25)
    goto(ard, 'z', -.2)


def get_inference_model(model_name="dotmodel.h5"):
    ''' Loads weights and returns an inference model '''

    inference_config = mark_dataset.InferenceConfig()
    model = modellib.MaskRCNN(mode="inference", 
                              config=inference_config,
                              model_dir=model_dir+'/logs')
    print("Loading weights from ", model_name)
    model.load_weights(model_name, by_name=True)
    return model

def get_mark_center(rois):
    centroids = []
    for dot in rois:
        centroids.append(np.stack([
            dot[1] + ((dot[3] - dot[1]) / 2.0),
            dot[0] + ((dot[2] - dot[0]) / 2.0),
        ], -1))
    return centroids

def find_dots(model, img):
    results = model.detect([img], verbose=1)
    r = results[0]
    if len(r['rois']) > 0:
        centroids = get_mark_center(r['rois'])
        return centroids, r

def get_cam_frame(cam):
    ret, frame = cam.read()
    return frame


if __name__ == '__main__':
    # Connect to Arduino
    ard = serial.Serial('COM5', 9600, timeout=5)
    time.sleep(2) # wait for Arduino

    # Open Webcam
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        raise Exception("Could not open video device")

    # Get model
    dotmodel = get_inference_model()

    homography = np.loadtxt('homography.txt')
    
    while True:
        img = get_cam_frame(video_capture)
        results = model.detect([img], verbose=1)
        r = results[0]
        centers = get_mark_center(r['rois'])
        try:
            b = np.array([[centers[0][0], centers[0][1] ]], dtype='float32')
            b = np.array([b])
            pointsOut = cv2.perspectiveTransform(b,homography)
            print (pointsOut)
            print (pointsOut[0][0][0]-current_point[0], pointsOut[0][0][1]-current_point[1])

            goto(pointsOut[0][0][0]-current_point[0], pointsOut[0][0][1]-current_point[1])
            current_point = [pointsOut[0][0][0], pointsOut[0][0][1]]
            
            erase()
        except:
            print ('no dot')

    # Close camera
    video_capture.release()




