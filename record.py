import cv2
import os
import argparse
from imutils import paths

# Save up to 10 images
img_counter = 0

# use name as folder name
name = input("Enter name: ")
folder = './dataset/{}'.format(name)



# Start the camera
cam = cv2.VideoCapture(0)
# Set video width
cam.set(3, 640) 
# Set video height
cam.set(4, 480)
# Get the pre-built classifier that had been trained on 3 million faces 
face_detector = cv2.CascadeClassifier('./xml/haarcascade_frontalface_default.xml')
eye_detector = cv2.CascadeClassifier('./xml/haarcascade_eye.xml')
smile_detector = cv2.CascadeClassifier('./xml/haarcascade_smile.xml')
# Create a window
cv2.namedWindow("Saving Images... (Press Escape to end)")


# Create a new folder for the new name
if not os.path.exists(folder):
    os.makedirs(folder)

while img_counter < 30:

    ret, frame = cam.read()
    cv2.imshow("frame", frame)

    if not ret:
        break
        
    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC preeesed
        print("Escape hit, closing...")
        break

    # if SPACE is pressed, look for the face/s in the image and classify them
    elif k%256 == 32:
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,      
            minSize=(30, 30)
            )

        for (x,y,w,h) in faces:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            eyes = eye_detector.detectMultiScale(
                roi_gray,
                scaleFactor= 1.5,
                minNeighbors=5,
                minSize=(5, 5),
                )
            
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
                   
            
            smile = smile_detector.detectMultiScale(
                roi_gray,
                scaleFactor= 1.5,
                minNeighbors=15,
                minSize=(25, 25),
                )
            
            for (xx, yy, ww, hh) in smile:
                cv2.rectangle(roi_color, (xx, yy), (xx + ww, yy + hh), (0, 255, 0), 2)
            
        img_name = "{}/{:04}.jpg".format(folder,img_counter)
        print("Press Enter the Space")
        cv2.imwrite(img_name, frame[y:y+h,x:x+w])
        print("{} written!".format(img_name))
        img_counter += 1

cam.release()
cv2.destroyAllWindows()