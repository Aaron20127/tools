#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import cv2 as cv
import numpy as np

import os
import sys

abspath = os.path.abspath(os.path.dirname(__file__))

class cameraUnistort():
    """Undistort image
    """
    def __init__(self, mtx, dist, image_size, black_roi=1):
        """Initialization, get the distortion correction of the re-mapping matrix
        @mtx: Intrinsic matrix, narray, shape(3,3)
        @dist: Distortion coefficient matrix, narray, shape(1,5), [k1, k2, p1, p2, k3]
        @image_size: length and width of image, (image.shape[1], image.shape[0])
        @blackRoi:1-completely retain black edge, 0-No black edges at all
        @return:None
        """
        mtx = np.array([[float(mtx[0]),              0,  float(mtx[2])],
                       [             0,  float(mtx[1]),  float(mtx[3])],
                       [             0,              0,             1]]) 
        dist = np.array([[float(dist[0]), float(dist[1]), 0, 0, 0]])

        ## Calculate the new camera matrix and the area without black edges
        newcameramtx, roi = cv.getOptimalNewCameraMatrix( \
            mtx, dist, image_size, black_roi, image_size)

        ## obtain re-mapping matrix, mapx, mapy, narray, shape(m,n)
        self.mapx, self.mapy = \
            cv.initUndistortRectifyMap(mtx, dist, None, newcameramtx, image_size, 5)
        
    def undistort(self, img):
        """undistort image
        @img: distortion image, narray, shape(m,n)
        @return: undistort image, narray, shape(m,n)
        """
        return cv.remap(img, self.mapx, self.mapy, cv.INTER_LINEAR)


def load_yaml(file_path):
    """Load yaml file
    @file_path   File path.
    """
    import yaml

    f = open(file_path, 'r')
    data = yaml.load(f)
    f.close()

    return data


def save_yaml(file_path, data):
    """Load yaml file
    @file_path   File path.
    """
    import yaml

    f = open(file_path, 'w')
    yaml.dump(data, f)  
    f.close()

    return data


def mkdir(path):
    """create folder
    @path   folder path.
    """
    path=path.strip()
    path=path.rstrip("\\")
    isExists=os.path.exists(path)
    if not isExists:
        os.makedirs(path.decode('utf-8')) 
        return True
    else:
        return False



