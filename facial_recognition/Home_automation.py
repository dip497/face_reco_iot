
# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import RPi.GPIO as GPIO
import speech_recognition as sr 

from gpiozero import AngularServo

#initialize servo motor
servo = AngularServo(4,initial_angle=90,min_pulse_width=0.0006,max_pulse_width=0.0023)

#setup IR sensor(input), Green LED (output), Red LED (output) resp.
GPIO.setup(23,GPIO.IN)
GPIO.setup(12,GPIO.OUT)
GPIO.setup(6,GPIO.OUT)



#function to read microphone
def takeCommand():
    #It takes microphone input from the user and returns string output
    r = sr.Recognizer()
    with sr.Microphone() as mic:
        print("Listening...")

        #after 0.2 sec it will start to recogine
        r.adjust_for_ambient_noise(mic,0.2)

        #for next  4 sec it will listen the microphone input 
        audio = r.listen(mic, 4)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
    except Exception:
        print("Say that again please...")
        return "None"
    return query

#function to check password
def check(code):
    # here Hello  is password to open the door
    if (code=="hello"):

        #open the door
        servo.angle=0
        time.sleep(5)


#function for setting up emails
def send_message(name):
    return requests.post(
        "https://api.mailgun.net/v3/YOUR_DOMAIN_NAME/messages",
        auth=("api", "8661701ffbf7d48ad61ede8433850aea-1831c31e-4828b48c"),
        files = [("attachment", ("image.jpg", open("image.jpg", "rb").read()))],
        data={"from": 'hello@example.com',
            "to": ["dipendra497@gmal.com"],
            "subject": "You have a visitor",
            "html": "<html>"  + " Someone has used your voice command.  </html>"})


while True:
    i=GPIO.input(23)
    # Any object is near IR sensor
    if i==1:
        # On green ligth
        GPIO.output(12,1)
    
#Initialize 'currentname' to trigger only when a new person is identified.
        currentname = "unknown"
#Determine faces from encodings.pickle file model created from train_model.py
        encodingsP = "encodings.pickle"

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
        print("[INFO] loading encodings + face detector...")
        data = pickle.loads(open(encodingsP, "rb").read())

# initialize the video stream and allow the camera sensor to warm up
# Set the ser to the followng
# src = 0 : for the build in single web cam, could be your laptop webcam
# src = 2 : I had to set it to 2 inorder to use the USB webcam attached to my laptop

        vs = VideoStream(usePiCamera=True).start()
        time.sleep(2)

# start the FPS counter
        fps = FPS().start()

# loop over frames from the video file stream
        while True:
	# grab the frame from the threaded video stream and resize it
	# to 500px (to speedup processing)
            frame = vs.read()
            frame = imutils.resize(frame, width=500)
	# Detect the fce boxes
            boxes = face_recognition.face_locations(frame)
	# compute the facial embeddings for each face bounding box
            encodings = face_recognition.face_encodings(frame, boxes)
            names = []

	# loop over the facial embeddings
            for encoding in encodings:
		# attempt to match each face in the input image to our known
		# encodings
                matches = face_recognition.compare_faces(data["encodings"],
                    encoding)
                name = "error" #if face is not recognized, then print Unknown

		# check to see if we have found a match
                if True in matches:
			# find the indexes of all matched faces then initialize a
			# dictionary to count the total number of times each face
			# was matched
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

			# loop over the matched indexes and maintain a count for
			# each recognized face face
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

			# determine the recognized face with the largest number
			# of votes (note: in the event of an unlikely tie Python
			# will select first entry in the dictionary)
                    name = max(counts, key=counts.get)

			#If someone in your dataset is identified, print their name on the screen
                    
                    if currentname != name:
                        currentname = name
                        print(currentname)
                        #Take a picture to send in the email
				        img_name = "image.jpg"
				        cv2.imwrite(img_name, frame)
				        print('Taking a picture.')
				
				        #Now send me an email to let me know who is at the door
				        request = send_message(name)
				        print ('Status Code: '+format(request.status_code))
                        #200 status code means email sent successfully
                        servo.angle = 0

                # If user is unknow 
                if(name =="error"):
                    # on Red ligth
                    GPIO.output(6,1) 
                    # listen microphone command
                    a = takeCommand()
                    # check with password
                    check(a)

                    # close door with servo motor
                    servo.angle=90

                    # turn off red ligth
                    GPIO.output(6,0)

		        # update the list of names
                names.append(name)

	# loop over the recognized faces
            for ((top, right, bottom, left), name) in zip(boxes, names):
		# draw the predicted face name on the image - color is in BGR
                cv2.rectangle(frame, (left, top), (right, bottom),
                    (0, 255, 225), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                    .8, (0, 255, 255), 2)

	# display the image to our screen
            cv2.imshow("Facial Recognition is Running", frame)
            key = cv2.waitKey(1) & 0xFF

	# when no object near camera turn off reconition
            i=GPIO.input(23)
            if i == 0:
                # turn off green ligth
                GPIO.output(12,0)
                break

	# update the FPS counter
            fps.update()
            

# stop the timer and display FPS information
        fps.stop()
        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
        cv2.destroyAllWindows()
        vs.stop()
    else:
        #turn off green ligth
        GPIO.output(12,0)