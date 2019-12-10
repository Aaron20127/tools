"""
A image control panel to interact with mouse. There are two type of button.

in the main thread to let the program exit normally when 'Ctrl+c' signal coming.
counter_button:
   [counter_button, name, (init, step, min, max), (shift_x, shift_y)]
   
   Paremeter:
        counter_button: button type.
        name:           button name.
        init:           starting value.
        step:           step size, it can be a decimals.
        min:            lower bound
        max:            uper bound
        shift_x:        coordinate of shift of button 
        shift_y:        coordinate of shift of button 
   Usage:
        click left mouse button: decrease couter
        click right mouse button: increse couter
        click mouse wheel: increase step size
        scroll the mouse wheel: accelerate the speed of count
one_click_button:
   ['one_click_button', 'name', (shift_x, shift_y)]
   Paremeter:
        one_click_button: button type.
        name:           button name.
        shift_x:        coordinate of shift of button 
        shift_y:        coordinate of shift of button 
   Usage:
        click left mouse button: make the value true 

API:
    opencv_button.get_value(): Get button value.
"""

import time
import threading
import signal
import sys
import cv2
import numpy as np
import math

class opencv_button:
    def __init__(self, buttons, panel_size=(400, 380)):
        """
            Parameters:
                buttons: add buttons, list.
                
                [
                        ['counter_button', 'camera1', [0, 1, 0,10000], [0, 0]],
                        ['one_click_button', 'save', (0, 50)]
                ]
                panel_size: size of control panel. list.
                
        """
        # 1.create control panel
        self.panel_size = panel_size
        self.create_control_button(buttons)

        # 2.stop signal
        self._stop = False

    def create_control_button(self, buttons):
        # 1. get button
        self.buttons = []
        for butt in buttons:
            new_button = None
            if butt[0] == 'counter_button':
                new_button = {
                    'type': butt[0],
                    'name': butt[1],
                    'value':butt[2][0],
                    'step':butt[2][1],
                    'min':butt[2][2],
                    'max':butt[2][3],
                    'position_shift':butt[3],
                    'rect_sub': [260+butt[3][0],30+butt[3][1],290+butt[3][0],55+butt[3][1]],
                    'rect_add': [300+butt[3][0],30+butt[3][1],330+butt[3][0],55+butt[3][1]],
                    'mult': 0,
                    'max_mult': len(str(int(butt[2][3])))-1
                }
            elif butt[0] == 'one_click_button':
                new_button = {
                    'type': butt[0],
                    'name': butt[1],
                    'value':False,
                    'position_shift':butt[2],
                    'rect': [260+butt[2][0],30+butt[2][1],330+butt[2][0],55+butt[2][1]]
                }
            else:
                print('error button type!')
                sys.exit()
            
            self.buttons.append(new_button)


    def update_panel(self):
        self.panel = np.zeros((self.panel_size[0],self.panel_size[1],3), np.uint8)
        for butt in self.buttons:
            if butt['type'] == 'counter_button':
                self.draw_counter_button(butt)
            elif butt['type'] == 'one_click_button':
                self.draw_one_click_button(butt)
            else:
                print('error button type!')
                sys.exit()


    def draw_counter_button(self, button):
        name = button['name']
        num = button['value']
        mult = str(button['mult'])
        x, y = button['position_shift']
        x11,y11,x12,y12 = button['rect_sub']
        x21,y21,x22,y22 = button['rect_add']

        str_num = str(num)
        str_max_num = str(button['max'])
        for i in range(len(str_max_num) - len(str_num)):
            str_num = ' ' + str_num

        cv2.putText(self.panel, name + ':',(10+x,50+y), cv2.FONT_HERSHEY_SIMPLEX, 0.8,(205,175,149),1,cv2.LINE_AA)
        cv2.putText(self.panel, str_num,(145+x,50+y), cv2.FONT_HERSHEY_SIMPLEX, 0.8,(100,255,255),1,cv2.LINE_AA)
        cv2.rectangle(self.panel,(x11,y11),(x12,y12),(205,175,149),-1)
        cv2.rectangle(self.panel,(x21,y21),(x22,y22),(205,175,149),-1)
        cv2.putText(self.panel,'-',(265+x,49+y), cv2.FONT_HERSHEY_SIMPLEX, 0.8,(60,60,60),1,cv2.LINE_AA)
        cv2.putText(self.panel,'+',(305+x,49+y), cv2.FONT_HERSHEY_SIMPLEX, 0.8,(60,60,60),1,cv2.LINE_AA)
        cv2.putText(self.panel,'x'+mult,(335+x,49+y), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(100,255,255),1,cv2.LINE_AA)


    def draw_one_click_button(self, button):
        name = button['name']
        save = ''
        if button['value'] == True:
            save = 'OK'
        x, y = button['position_shift']
        x11,y11,x12,y12 = button['rect']


        cv2.putText(self.panel, name + ':',(10+x,50+y), cv2.FONT_HERSHEY_SIMPLEX, 0.8,(205,175,149),1,cv2.LINE_AA)
        cv2.rectangle(self.panel,(x11,y11),(x12,y12),(205,175,149),-1)
        cv2.putText(self.panel, save, (277+x,50+y), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(60,60,60),2,cv2.LINE_AA)



    def run(self):
        cv2.namedWindow('panel')
        cv2.setMouseCallback('panel',self.event_callback)

        self.update_panel()
        cv2.imshow('panel',self.panel)
        cv2.waitKey(20)


    def event_callback(self, event, x, y, flags,param):
        if event == cv2.EVENT_LBUTTONUP or event == cv2.EVENT_MOUSEWHEEL:
            for i, butt in enumerate(self.buttons):
                if butt['type'] == 'counter_button':
                    x11,y11,x12,y12 = butt['rect_sub']
                    if x >= x11 and x <= x12 and y >= y11 and y <= y12:
                        new_num = self.buttons[i]['value'] - self.buttons[i]['step'] * pow(10, self.buttons[i]['mult'])
                        if new_num >= self.buttons[i]['min']:
                            self.buttons[i]['value'] = new_num

                    x11,y11,x12,y12 = butt['rect_add']
                    if x >= x11 and x <= x12 and y >= y11 and y <= y12:
                        new_num = self.buttons[i]['value'] + self.buttons[i]['step'] * pow(10,self.buttons[i]['mult'])
                        if new_num <= self.buttons[i]['max']:
                            self.buttons[i]['value'] = new_num

                if butt['type'] == 'one_click_button':
                    x11,y11,x12,y12 = butt['rect']
                    if x >= x11 and x <= x12 and y >= y11 and y <= y12:
                        self.buttons[i]['value'] = True

        if event == cv2.EVENT_MBUTTONUP:
            for i, butt in enumerate(self.buttons):
                if butt['type'] == 'counter_button':
                    x11,y11,x12,y12 = butt['rect_sub']
                    if x >= x11 and x <= x12 and y >= y11 and y <= y12:
                        new_mult = self.buttons[i]['mult'] + 1
                        if new_mult > self.buttons[i]['max_mult']:
                            self.buttons[i]['mult'] = 0
                        else:
                            self.buttons[i]['mult'] = new_mult

                    x11,y11,x12,y12 = butt['rect_add']
                    if x >= x11 and x <= x12 and y >= y11 and y <= y12:
                        new_mult = self.buttons[i]['mult'] + 1
                        if new_mult > self.buttons[i]['max_mult']:
                            self.buttons[i]['mult'] = 0
                        else:
                            self.buttons[i]['mult'] = new_mult


    def get_value(self):
        """ get button value
        @return: button value, list
        """
        # 1. run
        self.run()

        # 2. get value
        ret = []
        for butt in self.buttons:
            ret.append(butt['value'])
            if butt['type'] == 'one_click_button':
                butt['value'] = False
        return ret



if __name__ == "__main__":

    buttons = [
            ['counter_button', 'camera1', [9999, 1, 0,10000], [0, 0]],
            ['counter_button', 'camera2', [0, 1, 0,10000], [0, 50]],
            ['counter_button', 'camera3', [0, 1, 0,10000], [0, 100]],
            ['counter_button', 'label',   [0, 1, 0,10000], [0, 150]],
            ['one_click_button', 'save', (0, 200)]
    ]

    button = opencv_button(buttons)

    while True:
        camera1, camera2, camera3, label, save = button.get_value()
        print(camera1, camera2, camera3, label, save)
