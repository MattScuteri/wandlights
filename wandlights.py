from __future__ import print_function
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as num
import time
import cv2 as cv
import argparse
import io
from rpi_ws281x import *
import threading
import random

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
capture = cv.VideoCapture(0)
time.sleep(0.1)

LED_COUNT = 144
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

wandPosition = []
frame_width_half = 320
frame_height_half = 240

isOn = False

#background_subtract = cv.createBackgroundSubtractionMOG2()

def Stream():
    wandPosition = []

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        
        cv.imshow("Frame", image)
        
        key = cv.waitKey(1) & 0xFF

        rawCapture.truncate(0)
 
        if key == ord("q"):
            break
        
        findWand(image)

def findWand(image):   
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    lower_white = num.array([0,0,0], dtype=num.uint8)
    upper_white = num.array([0,0,255], dtype=num.uint8)
    
    white_mask = cv.inRange(hsv, lower_white, upper_white)
    ret, thresh = cv.threshold(white_mask, 127, 255, 0)
    trackedWand = cv.goodFeaturesToTrack(thresh, 5, .01, 30)
    moments = cv.moments(trackedWand)
    if moments["m00"] != 0:
        centerX = int(moments["m10"] / moments["m00"])
        centerY = int(moments["m01"] / moments["m00"])
    else:
        centerX, centerY = -1, -1
    
    cv.circle(white_mask, (centerX, centerY), 5, (255, 255, 255), -1)
    cv.putText(white_mask, "centroid", (centerX, centerY), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    
    if centerX > frame_width_half and centerY < frame_height_half and 'A' not in wandPosition:
        wandPosition.append('A')
    elif centerX > frame_width_half and centerY > frame_height_half and 'B' not in wandPosition:
        wandPosition.append('B')
    elif centerX < frame_width_half and centerY > frame_height_half and 'C' not in wandPosition:
        wandPosition.append('C')
    elif centerX < frame_width_half and centerY < frame_height_half and 'D' not in wandPosition:
        wandPosition.append('D')
        
    cv.imshow('white_mask', white_mask)
    
    if len(wandPosition) == 4:
        castSpell()
    else:
        print('still checking...')
    
def castSpell():
    global wandPosition
    print(wandPosition)
    turnOnLights = ['A', 'B', 'C', 'D']
    turnOffLights = ['D', 'C', 'B', 'A']
    
    if wandPosition == turnOnLights:
        print('LIGHTS ON!!!!')
        magicLightOn()
    else:
        print('No spell to cast...')
        wandPosition = []

def magicLightOn():
    global wandPosition
    wandPosition = []
    for num in range(30):
        color1 = random.randint(1,150)
        color2 = random.randint(1,150)
        color3 = random.randint(1,150)
        print(num)
        for x in range(0, LED_COUNT):
            strip.setPixelColor(x, Color(color1,color2,color3))    
            strip.show()
        
        if num == 29:
            magicLightOff()
            
def magicLightOff():
    for x in range(0, LED_COUNT):
        strip.setPixelColor(x, Color(0,0,0))
        
    strip.show()
    return


while True:
    magicLightOff()
    Stream()
    
    cv.destroyAllWindows()