#! /usr/bin/env python

import os
import random
import time
from Arduino import *
import alsaaudio
import wave
import random
from creds import *
import requests
import json
import re
from memcache import Client

#Settings
button = 203 #GPIO Pin with button connected
lights = [198, 199] # GPIO Pins with LED's conneted
# device = "plughw:CARD=Device,DEV=0" # Name of your microphone/soundcard in arecord -L

#Setup
recorded = False
servers = ["127.0.0.1:11211"]
mc = Client(servers, debug=1)
path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))



def internet_on():
    print "Checking Internet Connection"
    try:
        r =requests.get('https://api.amazon.com/auth/o2/token')
	print "Connection OK"
        return True
    except:
	print "Connection Failed"
    	return False

	
def gettoken():
	token = mc.get("access_token")
	refresh = refresh_token
	if token:
		return token
	elif refresh:
		payload = {"client_id" : Client_ID, "client_secret" : Client_Secret, "refresh_token" : refresh, "grant_type" : "refresh_token", }
		url = "https://api.amazon.com/auth/o2/token"
		r = requests.post(url, data = payload)
		resp = json.loads(r.text)
		mc.set("access_token", resp['access_token'], 3570)
		return resp['access_token']
	else:
		return False
		

def alexa():
	digitalWrite(lights[0], HIGH)
	url = 'https://access-alexa-na.amazon.com/v1/avs/speechrecognizer/recognize'
	headers = {'Authorization' : 'Bearer %s' % gettoken()}
	d = {
   		"messageHeader": {
       		"deviceContext": [
           		{
               		"name": "playbackState",
               		"namespace": "AudioPlayer",
               		"payload": {
                   		"streamId": "",
        			   	"offsetInMilliseconds": "0",
                   		"playerActivity": "IDLE"
               		}
           		}
       		]
		},
   		"messageBody": {
       		"profile": "alexa-close-talk",
       		"locale": "en-us",
       		"format": "audio/L16; rate=16000; channels=1"
   		}
	}
	with open(path+'recording.wav') as inf:
		files = [
				('file', ('request', json.dumps(d), 'application/json; charset=UTF-8')),
				('file', ('audio', inf, 'audio/L16; rate=16000; channels=1'))
				]	
		r = requests.post(url, headers=headers, files=files)
	if r.status_code == 200:
		for v in r.headers['content-type'].split(";"):
			if re.match('.*boundary.*', v):
				boundary =  v.split("=")[1]
		data = r.content.split(boundary)
		for d in data:
			if (len(d) >= 1024):
				audio = d.split('\r\n\r\n')[1].rstrip('--')
		with open(path+"response.mp3", 'wb') as f:
			f.write(audio)
		digitalWrite(lights[1], LOW)

		# os.system('mpg123 -q {}1sec.mp3 {}response.mp3 {}1sec.mp3'.format(path, path, path))
		os.system('madplay {}1sec.mp3 {}response.mp3 {}1sec.mp3 -o wave:- | aplay -D "plughw:CARD=Device,DEV=0" > /dev/null 2>&1'.format(path, path, path))
		digitalWrite(lights[0], LOW)
	else:
		digitalWrite(lights[1], LOW)
		for x in range(0, 3):
			time.sleep(.2)
			digitalWrite(lights[1], HIGH)
			time.sleep(.2)
			digitalWrite(lights[1], LOW)
		



def start():
	last = digitalRead(button)
	while True:
		val = digitalRead(button)
		while(digitalRead(button)==0):
			# we wait for the button to be pressed
			delay(10)
		digitalWrite(lights[1], HIGH)
		inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, device)
		inp.setchannels(1)
		inp.setrate(16000)
		inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
		inp.setperiodsize(500)
		audio = ""
		while(digitalRead(button)==1): # we keep recording while the button is pressed
			l, data = inp.read()
			if l:
				audio += data
		rf = open(path+'recording.wav', 'w')
		rf.write(audio)
		rf.close()
		inp = None
		alexa()

	

if __name__ == "__main__":
	pinMode(button, INPUT)
	pinMode(lights[0], OUTPUT)
	pinMode(lights[1], OUTPUT)
	digitalWrite(lights[0], LOW)
	digitalWrite(lights[1], LOW)
	while internet_on() == False:
		print "."
	token = gettoken()
	os.system('madplay {}1sec.mp3 {}hello.mp3 -o wave:- | aplay -D "plughw:CARD=Device,DEV=0" > /dev/null 2>&1'.format(path, path))
	for x in range(0, 3):
		time.sleep(.1)
		digitalWrite(lights[0], HIGH)
		time.sleep(.1)
		digitalWrite(lights[0], LOW)
	start()
