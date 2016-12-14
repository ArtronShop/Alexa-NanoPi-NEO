#!/usr/bin/python

# Codeing By IOXhop : www.ioxhop.com
# Sonthaya Nongnuch : www.fb.me/maxthai

import time

# Base Arduino
LOW    = 0
HIGH   = 1
INPUT  = 2
OUTPUT = 3

def fileWrite(path, data):
	try:
		f = open(path, 'w')
		f.write(str(data))
		f.close()
	except IOError as ValueError:
		if path != "/sys/class/gpio/export":
			print "Bug error [Write] : ", ValueError
			print "Path: ", path, " Data: ", data

def fileRead(path):
	try:
		f = open(path, 'r')
		data = f.read()
		f.close()
		return data;
	except IOError as ValueError:
		print "Bug error [Read] : ", ValueError
	except ValueError:
		print "Bug error [Read] : ", ValueError
	return "";

	
def pinMode(pin, mode):
	fileWrite("/sys/class/gpio/export", str(pin))
	if mode == 3:
		fileWrite("/sys/class/gpio/gpio" + str(pin) + "/direction", "out")
	else:
		fileWrite("/sys/class/gpio/gpio" + str(pin) + "/direction", "in")

def digitalWrite(pin, status):
	fileWrite("/sys/class/gpio/gpio" + str(pin) + "/value", status)
	
def digitalRead(pin):
	status = fileRead("/sys/class/gpio/gpio" + str(pin) + "/value")
	return int(status)
	
def delay(ms):
	time.sleep(float(int(ms) / 1000.0))