'''
calibration.py

Finds and saves the homomgrphy matrix between the 
CNC coordinates and the camera coordinates.

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
import eraser


def get_calibration_dots(numberx, numbery, spacingx, spacingy, spacingz):
    points = []
    direction = 1
    points.append(['z', spacingz])
    points.append(['z', -spacingz])
    for x in range(numberx):
        for y in range(numbery):
            points.append([0, direction*spacingy])
            points.append(['z', spacingz])
            points.append(['z', -spacingz])
        points.append([spacingx, 0])
        points.append(['z', spacingz])
        points.append(['z', -spacingz])
        direction = direction * -1
    return points

def draw_calibration_dots(ard, points):
    for x,y in points:
        goto(x,y)


if __name__ == '__main__':
     # Connect to Arduino
    ard = serial.Serial('COM5', 9600, timeout=5)
    time.sleep(2) # wait for Arduino

    # Draw the calibration dots on the whiteboard
    points = get_calibration_dots(5,5,2,2,.2)
    draw_calibration_dots(ard, points)

    # Move the marker out of the frame
    eraser.goto (ard, 2,2)

    model = eraser.get_inference_model()

    # Open Webcam
    video_capture = cv2.VideoCapture(1)
    if not video_capture.isOpened():
        raise Exception("Could not open video device")

    img = eraser.get_cam_frame(video_capture)

    # Close camera
    video_capture.release()

    results = model.detect([img], verbose=1)

    r = results[0]
    visualize.display_instances(img, r['rois'], r['masks'], r['class_ids'], 
                                classnames, r['scores'])

    centers = eraser.get_mark_center(r['rois'])

    src = []
    for x,y in centers:
        src.append([x,y])

    cncpoints = []
    for i in range(6):
        for j in range(5):
            cncpoints.append([j*2,i*2])

    # calculate matrix H
    h, status = cv2.findHomography(np.float32(src), np.float32(cncpoints), cv2.RANSAC)
    print (status)
    print (h)

    # Save the homography matrix
    np.savetxt('homography.txt', h)
