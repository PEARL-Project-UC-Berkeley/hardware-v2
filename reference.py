#!/usr/bin/env python3

import RPi.GPIO as GPIO
# Import libraries
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.widgets import Slider, Button
import serial
# import mysql.connector
import time
# firebase api in python
import pyrebase
# to get the hostname
import socket

if __name__ == '__main__':
	ser = serial.Serial('/dev/ttyUSB0',9600, timeout=1) 
	# ser.flush()
	ser.reset_input_buffer()
	config = {
		"apiKey": "",
		"authDomain": "pearl-labs.firebaseapp.com",
		"databaseURL": "https://pearl-labs-default-rtdb.firebaseio.com",
		"storageBucket": "pearl-labs.appspot.com"
	}
	firebase = pyrebase.initialize_app(config)
	db = firebase.database()
	# get hostname
	hostname = socket.gethostname()
	print("Hostname is: {}".format(hostname))
	
	all_devices = db.child("devices").get()
	valid_device = False
	for device in all_devices.each():
		if device.key() == hostname:
			valid_device = True
			break
	if valid_device == False:
		exit()
    
	stepperPositions = {}
	all_motors = db.child("devices").child(hostname).get()
	# print(all_motors)
	for motor in all_motors.each():
		stepperPositions[motor.key()] = 0.0
		# print(motor.key())

	print("initial stepperPos: {}".format(stepperPositions))
	ser.write("\n".encode('utf-8'))
	print("Controller enabled!")
 
	GPIO.setmode(GPIO.BOARD)
	power = 40
	GPIO.setup(power, GPIO.OUT)
	# GPIO.HIGH = 1, GPIO.LOW = 0. use these vals to update firebase as well
	# print(powerStatus.val())
	
	while True:
		time.sleep(2)
		for stepper in stepperPositions:
			newmotorPosObj = db.child("devices").child(hostname).child(stepper).child("motorPos").get()
			newmotorPos = newmotorPosObj.val()
			# print(newmotorPos)
			if newmotorPos != stepperPositions[stepper]:
				print("stepperID: {}, stepperPos: {}".format(stepper, newmotorPos))
				stepperPositions[stepper] = newmotorPos
				if stepper == "motor_1":
					stepper_id = 1
				else:
					stepper_id = 2
				inputString = "M{0}:{1}\n".format(stepper_id, newmotorPos)
				print(inputString)
				ser.write(inputString.encode('utf-8'))
				time.sleep(1)
		powerStatusObj = db.child("devices").child(hostname).child("power").get()
		newPowerStatus = powerStatusObj.val()
		if newPowerStatus != powerStatusObj.val():
			if powerStatusObj.val() == 1:
				GPIO.output(power, GPIO.HIGH)
				newPowerStatus = powerStatusObj.val()
			else:
				time.sleep(5)
				GPIO.output(power, GPIO.LOW)
				newPowerStatus = powerStatusObj.val()
			print("status:", powerStatusObj.val())
    
# print("stepper_id:{}, stepper_pos:{}, stepper_reset:{}, stepper_enable:{}".format(stepper_id, stepper_pos, stepper_reset, stepper_enable))
