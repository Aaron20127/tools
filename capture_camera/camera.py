#! /usr/bin/env python
# -*- encoding: utf-8 -*-

import cv2
import numpy as np
import time
import os
import sys
import signal
import threading
from time import sleep


abspath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(abspath + '/../../common/')

import utils

# replace image data between threads
img_global_dict = {}
thread_excute = True

def threadCameraRSTP (camera):
    """capture web camera
    @camera   camera configure information.
    """
    access =  'rtsp://' + camera['user'] + ':' + camera['passwd'] + \
              '@' + camera['ip'] + '//Streaming/Channels/1'
        
    # open vedio capture
    cap = cv2.VideoCapture(access)  
    if cap.isOpened():
        print('Connect to camera ' + camera['ip'] + ' successfully !')
    else:
        print('Cannot connect to camera ' + camera['ip'] + '! ')
        sys.exit(0)


    # obtain image size
    undistort = None
    dist_para = camera['undistort']
    if dist_para['enable']:
        img_size = (dist_para['image_size'][1],dist_para['image_size'][0])
        undistort = utils.cameraUnistort(dist_para['intrinsic_parameters'], \
            dist_para['distortion_parameters'], img_size, black_roi=dist_para['retain_black_edge'])
        
    # new image size
    new_img_size = None
    if camera['resize']['enable']:
        new_img_size = (camera['resize']['image_size'][1], camera['resize']['image_size'][0])

    # capture
    global img_global_dict
    global thread_excute
    while thread_excute:
        ret, img = cap.read()

        if not ret:
            print('read image fail')
        else:
            if camera['undistort']['enable']:
                img = undistort.undistort(img) 

            if camera['resize']['enable']:
                img = cv2.resize(img, new_img_size) 

            img_global_dict[camera['ip']]['image'] = img


def threadCameraUSB (camera):
    """capture usb camera
    @camera   camera configure information.
    """
    access = camera['port']
    # open video capture
    cap = cv2.VideoCapture(camera['access'])
    if cap.isOpened():
        print('Connect to camera usb ' + str(camera['port']) + ' successfully !')
    else:
        print('Cannot connect to camera usb ' + str(camera['port']) + '! ')
        sys.exit(0)

    # obtain image size
    undistort = None
    dist_para = camera['undistort']
    if dist_para['enable']:
        img_size = (dist_para['image_size'][1],dist_para['image_size'][0])
        undistort = utils.cameraUnistort(dist_para['intrinsic_parameters'], \
            dist_para['distortion_parameters'], img_size, black_roi=dist_para['retain_black_edge'])
        
    # new image size
    new_img_size = None
    if camera['resize']['enable']:
        new_img_size = (camera['resize']['image_size'][1], camera['resize']['image_size'][0])


    # publish 
    global img_global_dict
    global thread_excute
    while thread_excute:
        ret, img = cap.read()

        if not ret:
            rospy.loginfo('read image fail')
        else:
            if camera['undistort']['enable']:
                img = undistort.undistort(img) 

            if camera['resize']['enable']:
                img = cv2.resize(img, new_img_size) 

            img_global_dict[camera['port']]['image'] = img



def threadSaveImage(id):
    """save image
    @id camera id
    """

    # global
    global img_global_dict
    global thread_excute
    i = 0
    while thread_excute:
        if img_global_dict[id]['save'] > 0:
            save_dir = img_global_dict[id]['save_dir']
            img = img_global_dict[id]['image']
            cv2.imwrite(save_dir + '/' + str(i) + '.png', img)
            i += 1
            print(str(i) + '.png')
            img_global_dict[id]['save'] -= 1


def autoSave(ids, fps):
    """auto save images
    @ids  camera id
    @fps  How many images are saved per second
    """
    print('\nstart auto save image, fps = ' + str(fps) + ' ...')

    global img_global_dict
    global thread_excute
    interval = 1.0 / fps
    start_time = time.time()

    while thread_excute:
        end_time = time.time()
        if (end_time - start_time) > interval:
            for id in ids:
                img_global_dict[id]['save'] += 1
            start_time = end_time


def manualSave(ids):
    """auto save images
    @ids  camera id
    @fps  How many images are saved per second
    """
    print('\nplease press Enter to save image ...')
    global thread_excute
    while thread_excute:
        str = raw_input()
        if str == '':
            for id in ids:
                img_global_dict[id]['save'] += 1


def captureImage(cfg):
    """capture and save image 
    @cfg  configure file
    """
    global img_global_dict
    ids = []
    thread_ids = []

    ## create save dir
    base_dir = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime(time.time()))
    full_dir = abspath + '/images/' + base_dir
    utils.mkdir(full_dir)

    ## 1.start camera threads and save threads

    for camera in cfg['cameras']:
        id = None
        if camera['enable'] == True:
            if camera['type'] == "web_camera":
                id = camera['ip']
                # capture web camera thread
                thread_ids.append(threading.Thread(target=threadCameraRSTP,args=(camera,)))

            elif camera['type'] == "usb_camera":
                id = camera['port']
                # capture usb camera thread
                thread_ids.append(threading.Thread(target=threadCameraUSB,args=(camera,)))

            # save image thread
            thread_ids.append(threading.Thread(target=threadSaveImage,args=(id,))) 

            ids.append(id)
            save_dir = full_dir + '/' + id
            print(id + ', save path: ' + save_dir)
            utils.mkdir(save_dir)

            img_global_dict[id] = {
                'image' : None,
                'save'  : 0,
                'save_dir' : save_dir
            }

    # start thread
    for thread in thread_ids:
        thread.setDaemon = True
        thread.start()

    time.sleep(3)

    # start save
    if cfg['general']['autosave'] == True:
        autoSave(ids, cfg['general']['fps'])
    else:
        manualSave(ids)


def run():
    # signal handle
    def handler(sig, argv):
        global thread_excute
        thread_excute = False
        print('\nexit!')
        # os.kill(os.getpid(),signal.SIGKILL)

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGQUIT, handler)

    # read configure
    file_path = abspath + '/cfg.yaml'
    cfg = utils.load_yaml(file_path)

    # start capture image
    captureImage(cfg)


if __name__ == '__main__':
    run()


