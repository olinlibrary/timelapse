#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import pickle
import flickr_api
import picamera
from datetime import datetime as d
import os
import sys
import logging

GPIO.setmode(GPIO.BCM)
PIR_PIN = 4

GPIO.setup(PIR_PIN, GPIO.IN)
motion_detected = False

def motion_cbk(PIR_PIN):
	global motion_detected
	motion_detected = True

logging.basicConfig(filename='time_lapse.log', level=logging.DEBUG)

c = pickle.load(open('credentials.p', 'rb'))

API_KEY = c.get('API_KEY')
API_SECRET = c.get('API_SECRET')
USER_ID = c.get('USER_ID')
PHOTO_SET_ID = c.get('PHOTO_SET_ID')
DEFAULT_INTERVAL = 3 #in minutes

flickr_api.set_keys(api_key = API_KEY, api_secret = API_SECRET)
a = flickr_api.auth.AuthHandler.load('/home/pi/timelapse/owl_auth_token')
flickr_api.set_auth_handler(a)
user = flickr_api.test.login()
photosets = user.getPhotosets()
for p in photosets:
	if p.id == PHOTO_SET_ID:
		break

if len(sys.argv) == 2:
	interval = int(sys.argv[1])
else:
	interval = DEFAULT_INTERVAL

camera = picamera.PiCamera()
camera.resolution = (2592, 1944)
img_idx = 0

try:
    GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=motion_cbk)
    while True:
        n = d.now()
        if motion_detected:
            try:
                camera.led = True
                fname = n.strftime('%Y%m%d%H%M') + '.jpg'
                camera.capture(fname)
                photo = flickr_api.upload(photo_file=fname)
                p.addPhoto(photo_id = photo.id)
                os.remove(fname)
                camera.led = False
                motion_detected = False
            except:
                print("Encountered an exception")
                e = sys.exc_info()[0]
                logging.error(e)
                camera.led = False

            time.sleep(interval*60)

except KeyboardInterrupt:
    print("Quitting...")
    GPIO.cleanup()
