import time
import serial
import struct
import sys

# to import auto_robot.py
#
# import autonomous_robot
# import sys
# sys.path.instert(0,'/home/pi/dev/ball_tracking/utils')
#
# auto_robot.forward()
# auto_robot.reverse()
# auto_robot.left()
# auto_robot.right()
#
# Serial UART to Arduino
# for pi need to run this first in order to access the serial port
# better way would be to add pi to the group
# sudo chmod 666 /dev/ttyS0
arduino = serial.Serial('/dev/ttyS0', baudrate=9600, timeout=3.0)

# variables that let the Arduino motor drive know what direction to go
#
# forward = 4
# right = 2
# left = 1
# reverse = 8
# i = 0
#
# Functions
# moves robot forward
def forward():
    i = 0
    forward = 4
    while i < 10:
        arduino.write(struct.pack('>B',forward))
        i += 1
        time.sleep(0.04)
# robot goes in reverse
def reverse():
    i = 0
    reverse = 8
    while i < 25:
        arduino.write(struct.pack('>B',reverse))
        i += 1
        time.sleep(0.04)
# turns robot left
def left():
    i = 0
    left = 1
    while i < 7:
        arduino.write(struct.pack('>B',left))
        i += 1
        time.sleep(0.04)
# turns robot right
def right():
    i = 0
    right = 2
    while i < 7:
        arduino.write(struct.pack('>B',right))
        i += 1
        time.sleep(0.04)


        # arduino.close()
