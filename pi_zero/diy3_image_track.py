#
# author: Paul Davis
# email: pdavis39@gmail.com
# created: 2/29/2018
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#from pivideostream import PiVideoStream
from __future__ import division
import datetime
import time
import cv2
import serial
import time
import sys
import os
import paramiko
from collections import deque
from picamera.array import PiRGBArray
from picamera import PiCamera
from pyimagesearch.tempimage import TempImage
import hashlib
import uuid
import json
import paho.mqtt.publish as publish
import numpy as np
import requests
import struct
import io

sys.path.insert(0,'/home/pi/dev/ball_tracking/utils')
import auto_drive
#import ultrasonic_distance
import ultra_distance

# Define Variables
MQTT_HOST = <"hostName">
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 45
MQTT_TOPIC = "robotPayload/image-metadata"

# where we last left off on the blockchain CapturedImage num
ciid = 4687


# from gpiozero import DistanceSensor
# import RPi.GPIO as GPIO
from multiprocessing import Process, Queue
import warnings
warnings.filterwarnings('default', category=DeprecationWarning)
# camera settings
camera = PiCamera()
# camera.resolution = (640, 480)
camera.resolution = (320, 240)
camera.framerate = 60
#rawCapture = PiRGBArray(camera, size=(640, 480))
rawCapture = PiRGBArray(camera, size=(320, 240))
SCREEN_WIDTH = 240
# servo settings
# GREEN_PIN = 22 # GPIO
# RED_PIN = 27 # GPIO
# print('Setting up wiring pi'),
# wiringpi.wiringPiSetupGpio()
# wiringpi.pinMode(GREEN_PIN, 1)
# wiringpi.pinMode(RED_PIN, 1)
# print('Done setting up wiring pi')
# how to find tty - dmesg | grep tty
print("Starting to set up serial connection to Arduino")

arduino = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=3.0)
print("Setting up serial connection to Arduino complete")
print("camera warming up...")
time.sleep(2.5)
print("camera awake...")
pts = deque()
# code to pick hsv color
# green = np.uint8([[[0,255,0 ]]])
# hsv_green = cv2.cvtColor(green,cv2.COLOR_BGR2HSV)
# print hsv_green
#lower_blue = (110,50,50)
#upper_blue = (130,255,255)
# tennis ball
#lower_green = (29,86,6)
#upper_green = (64,255,255)
# pickup truck photo
#lower_red = (169,100,100)
#upper_red = (189,255,255)
# websiste https://pastebin.com/WVhfmphS
# define the lower and upper boundaries of the colors in the HSV color space
lower = {'red':(169, 100, 100), 'green':(29, 86, 6), 'blue':(110, 50, 50)}
upper = {'red':(189,255,255), 'green':(64,255,255), 'blue':(130,255,255)}

# define standard colors for circle around the object
colors = {'red':(0,0,255), 'green':(0,255,0), 'blue':(255,0,0), 'yellow':(0, 255, 217), 'orange':(0,140,255)}

start_time = time.time()
#---------------------------------------------------------------------------------------------------------#
# set environment
center = (0,0)
center_x = 120
center_y = 160
cnts = 0
posX = 0
posY = 0
cnt_x = 0
cnt_y = 0
servo_x = 60
servo_y = 70
arduino.write('60P'.encode())
arduino.write('70T'.encode())
tmp_x = 0
tmp_y = 0
imageFlag = 'False'

#---------------------------------------------------------------------------------------------------------#
# loop over the frames from the video stream
while True:
    print("starting for loop")
    print("checking distance sensor is working")
 #   dist = ultrasonic_distance.distance()
    dist = ultra_distance.distance()
    #dist = 5.2
    print("Measured Distance = %.1f inches" % dist)

    for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        frame = f.array
        rawCapture.seek(0)
        rawCapture.truncate()
        # frame = imutils.resize(frame, width=240)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # contruct a mask for the color green, then perform a series of dilations and erosions to remove
        # any blobs left in the mask
        for key, value in upper.items():
        # construct a mask for the color from dictionary`1, then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
            kernel = np.ones((9,9),np.uint8)
            mask = cv2.inRange(hsv, lower[key], upper[key])
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # if statement to capture which color mask is used


            #mask = blue_mask + green_mask + red_mask

            #mask = cv2.erode(mask,None, iterations=2)
            #mask = cv2.dilate(mask, None, iterations=2)
            # find countoursr in the mask and initilze the current (x,y) center of the ball
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            # print cnts
            center = None
            #only proceed if at least on contour was found
            if len(cnts) > 0:
                # find largest contour in the mask, then use it to compute the min enclosing circle and centroid
                c = max(cnts, key=cv2.contourArea)
                ((x,y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                #  moments = M
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                # area = moments['m00']
                # Calculating the center postition of the blob
                # only proceed if the radius meets a minimum size
                if radius > 10:
                    #draw the circle and centriod on the frame, then update list of tracked points

                    # add text to circle frame with distance sensor output
                    cv2.circle(frame, (int(x),int(y)), int(radius), colors[key],2)
                    cv2.circle(frame, center, 5,(0,0,255), -1)
                    posX = center[0]
                    posY = center[1]
                    print('The center is', center, 'initial posX', posX, 'initial posY', posY)


                    # capture the image for classification by jetson tx2
                    # probably need to set a flag to ensure that multiple photos are not taken of the same image
                    if radius < 83:
                    	imageFlag = 'False'
                       # print("Measured Distance = %.1f inches" % dist)
                    if radius > 83 and imageFlag == 'False':
                   #     print("Measured Distance = %.1f inches" % dist)
                        # need to come up with a to name image
                        color = key
                        dir_name = '/tmp'
                        format = 'jpg'
                        base_filename = color + "_" + str(uuid.uuid4().hex)
                        src = os.path.join(dir_name, base_filename + "." + format)
                        cv2.imwrite(src, frame)

                        hash = hashlib.md5(src.encode('utf-8')).hexdigest()

                        dst = os.path.join('/home/nvidia/dev/fooler/images/diy3/' + base_filename + "." + format)
                        # mqtt_message = json.dumps({"hash": hash,"image_location": dst, "color": color, "robot": "diy3" })
                       # publish.single(MQTT_TOPIC, mqtt_message, hostname=MQTT_HOST)
                        # Open a transport
                        hostname = <"hostName">
                        port = 22
                        # Auth
                        password = <"password">
                        username = <"userName">
                        client = paramiko.SSHClient()
                        client.load_system_host_keys()
                        print (" Connecting to %s \n with username=%s... \n" %(hostname,username))
                        t = paramiko.Transport(hostname, port)
                        t.connect(username=username,password=password)
                        sftp = paramiko.SFTPClient.from_transport(t)
                        print ("Copying file: %s to path: %s" %(src, dst))
                        sftp.put(src, dst)
                        sftp.close()
                        t.close()
                        print('image transer success')
                       # mqtt_message = json.dumps({"hash": hash,"image_location": dst, "color": color, "robot": "diy3" })
                        mqtt_message = json.dumps({"hash": hash,"image_location": dst, "color": color, "robot": "resource:com.diy3.Robot#1152" , "asset": "resource:com.diy3.CapturedImage#"+str(ciid)})
                        publish.single(MQTT_TOPIC, mqtt_message, hostname=MQTT_HOST)
                        # this sends the data to the blockchain
                        # This send the results to Composer Rest Server
                        url = "http://devmac:3000/api/com.diy3.CapturedImage"

                      #  "'"'+str(image_location)+'"'"
                        payload = "{\n   \"$class\": \"com.diy3.CapturedImage\",\n   \"capturedImageId\": "'"'+str(ciid)+'"'",\n   \"robot\": \"resource:com.diy3.Robot#1152\",\n   \"objectColor\": "'"'+str(color)+'"'",\n   \"objectState\":\"UNKNOWN\",\n   \"imageHash\":  "'"'+hash+'"'",\n   \"imageLocation\": "'"'+dst+'"'" \n }"
                        headers = {
                            'Content-Type': "application/json",
                            'Cache-Control': "no-cache",
                        }

                        response = requests.request("POST", url, data=payload, headers=headers)

                        print(response.text)
                        ciid += 1
                        #mqtt_message = json.dumps({"hash": hex,"image_location": dst, "color": color, "robot": "diy3" })
                        time.sleep(2)
                        imageFlag = 'True'

                    # bottom left
                    if posX > 0 and posX < 160 and posY > 120 and posY < 240:
                        print('bottom left - servo_x ', servo_x,'servo_y ', servo_y)
                        tmp_x = 160 - posX
                        print('The x position for tmp_x is:', tmp_x)
                        tmp_x = tmp_x / 80
                        print('tmp_x', round(tmp_x,0) )
                        print('rounded tmp_x', tmp_x)
                        tmp_x = round(tmp_x)
                        servo_x = servo_x - tmp_x
                        p = str(servo_x) + 'P'
                        print(p)
                        print('the radius is: ', radius)
                        print('the radius is: ', radius)
                        arduino.write(p.encode())
                        tmp_y = posY - 120
                        print('The y position for tmp_y is: ',tmp_y)
                        tmp_y = tmp_y / 60
                        tmp_y = round(tmp_y)
                        servo_y = servo_y + tmp_y
                        p = str(servo_y) + 'T'
                        arduino.write(p.encode())
                        print(p)
                        print('the radius is: ', radius)
                        print('bottom left')
                        pts.appendleft(center)
                        cv2.imshow('Object Tracking Frame', frame)
                        key = cv2.waitKey(1) & 0xFF
                    # top left
                    if posX > 0 and posX < 160 and posY > 0 and posY < 120:
                        print('top left - servo_x ', servo_x,'servo_y ', servo_y)
                        tmp_x = 160 - posX
                        print('The x position for tmp_x is:', tmp_x)
                        tmp_x = tmp_x / 80
                        print('tmp_x', tmp_x)
                        tmp_x = round(tmp_x)
                        servo_x = servo_x - tmp_x
                        print('servo_x', servo_x)
                        p = str(servo_x) + 'P'
                        print(p)
                        print('the radius is: ', radius)
                        arduino.write(p.encode())
                        tmp_y = 120 - posY
                        print('The y position for tmp_y is: ',tmp_y)
                        tmp_y = tmp_y / 60
                        tmp_y = round(tmp_y)
                        #  tmp_y = int(tmp_y) * 9
                        print(tmp_y, 'tmp_y')
                        servo_y = servo_y - tmp_y
                        # servo_y = servo_y - tmp_y
                        p = str(servo_y) + 'T'
                        arduino.write(p.encode())
                        print(p)
                        print('the radius is: ', radius)
                        print('top left')
                        # value = colors[key]
                      #  print('key', key)
                      #  print('colors key', colors[key])
                        pts.appendleft(center)
                        cv2.imshow('Object Tracking Frame', frame)
                        key = cv2.waitKey(1) & 0xFF
                    # top right
                    if posX > 160 and posX < 320 and posY > 0 and posY < 120:
                        print('top right - servo_x ', servo_x,'servo_y ', servo_y)

                        tmp_x = posX - 160
                        print('The x position for tmp_x is:', tmp_x)
                        tmp_x = tmp_x / 80
                        print('tmp_x/80', tmp_x)
                        #   tmp_x = tmp_x * 9
                        #   print 'tmp_x * 9 = ', tmp_x
                        tmp_x = round(tmp_x)
                        servo_x = servo_x + tmp_x
                        p = str(servo_x) + 'P'
                        arduino.write(p.encode())
                        print(p)
                        print('the radius is: ', radius)
                        tmp_y = 120 - posY
                        print('The y position for tmp_y is: ',tmp_y)
                        tmp_y = tmp_y / 60
                        print('tmp_y/60', tmp_y)
                        tmp_y = round(tmp_y)
                        #     tmp_y = tmp_y * 9
                        #   print 'tmp_y * 9 = ', tmp_y
                        servo_y = servo_y - tmp_y
                        print('servo_y', servo_y)
                        p = str(servo_y) + 'T'
                        arduino.write(p.encode())
                        print(p)
                        print('the radius is: ', radius)
                        print('top right')
                        pts.appendleft(center)
                        cv2.imshow('Object Tracking Frame', frame)
                        key = cv2.waitKey(1) & 0xFF
                    # bottom right
                    if posX > 160 and posX < 320 and posY > 120 and posY < 240:
                        print('bottom right - servo_x ', servo_x,'servo_y ', servo_y)
                        tmp_x = posX - 160
                        print('The x position for tmp_x is:', tmp_x)
                        tmp_x = tmp_x / 80
                        tmp_x = round(tmp_x)
                        servo_x = servo_x + tmp_x
                        p = str(servo_x) + 'P'
                        arduino.write(p.encode())
                        print('this is p for x: ',p)
                        print('the radius is: ', radius)
                        arduino.write(p.encode())
                        tmp_y = posY - 120
                        print('The y position for tmp_y is: ',tmp_y)
                        tmp_y = tmp_y / 60
                        tmp_y = round(tmp_y)
                        servo_y = servo_y + tmp_y
                        p = str(servo_y) + 'T'
                        arduino.write(p.encode())
                        print('this is p for y: ',p)
                        print('the radius is: ', radius)
                        print('bottom right')
                    if posX == 160 and posY == 120:
                        print('i am in the middle')
                        print('the radius is: ', radius)
                        pts.appendleft(center)
                        cv2.imshow('Object Tracking Frame', frame)
                        key = cv2.waitKey(1) & 0xFF
