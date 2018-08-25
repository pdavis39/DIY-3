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
#Libraries
import RPi.GPIO as GPIO
import time


#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

#set GPIO Pins
#GPIO_TRIGGER = 23
#GPIO_ECHO = 24
GPIO_TRIGGER = 24
GPIO_ECHO = 23
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setwarnings(False)
time.sleep(1)
dist = 0

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    

    GPIO.output(GPIO_TRIGGER, False)
   

    StartTime = time.time()
    StopTime = time.time()
   # print("Waiting for sensor to settle")

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # StopTime = time.time()    

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    time.sleep(.5)    

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    print("bottom of loop")

    return distance

if __name__ == '__main__':
    try:
        while True:
            dist = distance() * 0.393701
            print("Measured Distance = %.1f in" % dist)
            time.sleep(1)

         #   Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
