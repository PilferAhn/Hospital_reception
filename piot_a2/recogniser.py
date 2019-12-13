'''
Acknowledgements
	- recogniser.py file is provided from RMIT PIoT staff for educational purposes only
'''
# USAGE
# With default parameters
# 		python3 03_recognise.py
# OR specifying the encodings, screen resolution, output video and display
# 		python3 03_recognise.py -e encodings.pickle -r 240 -o output/capture.avi -y 1

## Acknowledgement
## This code is adapted from:
## https://www.pyimagesearch.com/2018/06/18/face-recognition-with-opencv-python-and-deep-learning/

# import the necessary packages
from imutils.video import VideoStream
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2

def recognise_face():

	# construct the argument parser and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-e", "--encodings", default='./pickle/encodings.pickle',
		help="path to serialized db of facial encodings")

	ap.add_argument("-em", "--emotion_encodings", default='./pickle/emotion_encodings.pickle',
		help="path to serialized db of facial encodings")

	ap.add_argument("-r", "--resolution", type=int, default=250,
	        help="Resolution of the video feed")
	ap.add_argument("-o", "--output", type=str,
		help="path to output video")
	ap.add_argument("-y", "--display", type=int, default=1,
		help="whether or not to display output frame to screen")
	ap.add_argument("-d", "--detection-method", type=str, default="cnn",
		help="face detection model to use: either 'hog' or 'cnn'")
	args = vars(ap.parse_args())

	# load the known faces and embeddings
	print("[INFO] loading encodings...")
	# face pickle
	# smail pickle
	data = pickle.loads(open(args["encodings"], "rb").read())

	feeling_data = pickle.loads(open(args["emotion_encodings"], "rb").read())

	# initialize the video stream and pointer to output video file, then
	# allow the camera sensor to warm up
	print("[INFO] starting video stream...")
	vs = VideoStream(src=0).start()
	writer = None
	time.sleep(2.0)

	isPatient = 0
	isUnknown = 0

	isAngry = 0
	isNeutral = 0

	client_name = ""
	client_feeling = ""
	# loop over frames from the video file stream
	while isAngry < 30 and isNeutral < 30:
		# grab the frame from the threaded video stream
		frame = vs.read()
		

		# convert the input frame from BGR to RGB then resize it to have
		# a width of 240px (to speedup processing)
		rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		rgb = imutils.resize(frame, width=args["resolution"])
		r = frame.shape[1] / float(rgb.shape[1])

		# detect the (x, y)-coordinates of the bounding boxes
		# corresponding to each face in the input frame, then compute
		# the facial embeddings for each face
		boxes = face_recognition.face_locations(rgb, model=args["detection_method"])		
		encodings = face_recognition.face_encodings(rgb, boxes)
		names = []
		feelings = []

		# loop over the facial embeddings
		for encoding in encodings:
			# attempt to match each face in the input image to our known
			# encodings
			matches = face_recognition.compare_faces(data["encodings"], encoding, tolerance=0.4)
			name = "Unknown"	
			# check to see if we have found a match
			if True in matches:
				# find the indexes of all matched faces then initialize a
				# dictionary to count the total number of times each face
				# was matched
				matchedIdxs = [i for (i, b) in enumerate(matches) if b]
				counts = {}
				
				# loop over the matched indexes and maintain a count for each recognized face face
				for i in matchedIdxs:
					name = data["names"][i]
					counts[name] = counts.get(name, 0) + 1

				name = max(counts, key=counts.get)	
			
			if isPatient < 15 and isUnknown < 15:
				if name == "Unknown":
					isUnknown += 1
				else:
					isPatient += 1
				names.append(name)
				client_name = name
				print("name: " + name)

		# loop over the recognized faces
		for ((top, right, bottom, left), name) in zip(boxes, names):
			# rescale the face coordinates
			top = int(top * r)
			right = int(right * r)
			bottom = int(bottom * r)
			left = int(left * r)

			# draw the predicted face name on the image
			cv2.rectangle(frame, (left, top), (right, bottom),
				(0, 255, 0), 2)
			y = top - 15 if top - 15 > 15 else top + 15
			cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
				0.75, (0, 255, 0), 2)



		# looping for cathcing client emotions
		# emotion has two conditions
		# Neutral && Angry
		# Notify to doctor the client condition
		for encoding in encodings:

			feeling_matches = face_recognition.compare_faces(feeling_data["emotion_encodings"], encoding, tolerance=0.35)
			# default client emotion is setted to Neutral	
			feeling = "Neutral"

			if True in feeling_matches:
				matchedIdxs = [i for (i, b) in enumerate(feeling_matches) if b]
				counts = {}

				for i in matchedIdxs:

					feeling = feeling_data["feelings"][i]
					#print("test: " + feeling)
					counts[feeling] = counts.get(feeling, 0) + 1

				feeling = max(counts, key=counts.get)

			# jimin folder face is setting to default face. 
			if feeling == "jimin":
				feeling = "Neutral"
				isAngry += 1
			else:
				feeling = "Angry"
				# 
				isNeutral += 1

			feelings.append(feeling)
			print("Emtion: " + feeling)
			client_feeling = feeling
		

		# if the video writer is None *AND* we are supposed to write
		# the output video to disk initialize the writer
		if writer is None and args["output"] is not None:
			fourcc = cv2.VideoWriter_fourcc(*"MJPG")
			writer = cv2.VideoWriter(args["output"], fourcc, 20,
				(frame.shape[1], frame.shape[0]), True)

		# if the writer is not None, write the frame with recognized
		# faces to disk
		if writer is not None:
			writer.write(frame)

		# check to see if we are supposed to display the output frame to
		# the screen
		if args["display"] > 0:
			cv2.imshow("Frame", frame)
			key = cv2.waitKey(1) & 0xFF

			# if the `q` key was pressed, break from the loop
			# return client condition to server
			# Angry or Neutral
			if key == ord("q") or isAngry == 15 or isNeutral == 15:
				return client_name, client_feeling



	# do a bit of cleanup
	cv2.destroyAllWindows()
	vs.stop()

	# check to see if the video writer point needs to be released
	if writer is not None:
		writer.release()

if __name__ == '__main__':
	recognise_face()
