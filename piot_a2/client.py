import os
import grpc

import iot_pb2
import iot_pb2_grpc
from recogniser import recognise_face

def run():
	'''
	Patient (client 1) script. Runs recognise_face function from recogniser.py
	and check if the person's face has already been trained in the database (encodings.pickle).
	Afterwards, it sends the patient name to Clerk end (server).
	'''
	ip = input("Enter MAPS server's IP address: ")
	# receive facial recognition name here
	patient_name, patient_feeling = recognise_face()
	with grpc.insecure_channel('{}:50051'.format(ip)) as channel:
		stub = iot_pb2_grpc.PatientRecogniserStub(channel)
		stub.VerifyPatient(iot_pb2.PatientDetails(name=patient_name, feeling=patient_feeling))

if __name__ == '__main__':
	run()
