import os
import grpc

import iot_pb2
import iot_pb2_grpc

from gtts import gTTS
from pydub import AudioSegment
import subprocess

def run():
	'''
	Doctor (client 2) script. It receives patient name and say the patient has arrived.
	gTTS (Google Text To Speech) API has been used.
	'''
	ip = input("Enter MAPS server's IP address: ")
	channel = grpc.insecure_channel('{}:50051'.format(ip))
	stub = iot_pb2_grpc.PatientRecogniserStub(channel)
	while True:
		user = stub.notifyDoctor(iot_pb2.Empty())
		if user.name != "":
			print(user.name)
			print(user.feeling)
			received_msg = 'Patient' + user.name + ' has arrived.'
			if user.feeling == "Angry":
				received_msg = received_msg + ' But' + user.name + ' is ' + user.feeling + '. So please treat ' + user.name + ' carefully.'
			else:
				received_msg = received_msg + ' And ' + user.name + ' looks fine today.'
				# tts = gTTS(text='Patient ' + user.name + ' has arrived. But ' + user.name + 'is ' + user.feeling 
				# 			+ '. So please treat him carefully.', lang='en')
			# elif user.feeling == "Neutral":
			# 	
			tts = gTTS(text=received_msg, lang='en')
			stub.VerifyPatient(iot_pb2.PatientDetails(name="", feeling=""))
			# Run text to speech code
			tts.save("arrival.mp3")
			os.system("mpg321 arrival.mp3")
			os.remove("arrival.mp3")

if __name__ == '__main__':
	run()
