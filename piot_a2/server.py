from concurrent import futures
import os
import time
from sense_hat import SenseHat
import grpc

import iot_pb2
import iot_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
client_name = ""
client_feeling = ""
sense = SenseHat()
red = (255, 0, 0)
green = (0, 255, 0)

class PatientVerifier(iot_pb2_grpc.PatientRecogniserServicer):
	'''
	Defines functions to connect both clients and server.
	unary-unary approach has been applied.
	'''

	def __init__(self, client_name, client_feeling):
		'''
		Constructor to get patient name from client 1 (patient on local end) 
		to the server then pass the name to client 2 (doctor on server side)
		'''
		self.client_name = client_name
		self.client_feeling = client_feeling

	def VerifyPatient(self, request, context):
		'''
		Check if the patient is valid or unknown person and pass the data to the clerk (server end)
		'''
		received = iot_pb2.PatientDetails(name=request.name, feeling=request.feeling)
		print(received)
		self.client_name = request.name
		self.client_feeling = request.feeling

		# check if facial recognition detect a correct patient
		if request.name == "Unknown":
			sense.clear(red)
			time.sleep(2)
			sense.clear()
		else:
			sense.clear(green)
			time.sleep(2)
			sense.clear()

		return iot_pb2.PatientDetails()

	def notifyDoctor(self, request, context):
		'''
		Notify the information of the patient to the doctor end (another client)
		'''
		# check if unknown person have arrived
		if self.client_name == "Unknown":
			return iot_pb2.PatientDetails(name="", feeling="")	
		return iot_pb2.PatientDetails(name=self.client_name, feeling=self.client_feeling)


def serve():
	'''
	Run gRPC for client-server communications
	'''
	ip = os.popen('hostname -I').read()
	print(ip)
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
	iot_pb2_grpc.add_PatientRecogniserServicer_to_server(PatientVerifier(client_name, client_feeling), server)
	server.add_insecure_port('{}:50051'.format(ip))
	server.start()
	try:
		while True:
			time.sleep(_ONE_DAY_IN_SECONDS)
	except KeyboardInterrupt:
		server.stop(0)

if __name__ == '__main__':
	serve()