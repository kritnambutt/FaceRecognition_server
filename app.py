# import the necessary packages
from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import face_recognition
import numpy as np
from random import random
import cv2
from time import sleep
from threading import Thread, Event
import redis
import base64

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=None, logger=True, engineio_logger=True) # CORS

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

# def randomNumberGenerator():
#     """
#     Generate a random number every 1 second and emit to a socketio instance (broadcast)
#     Ideally to be run in a separate thread?
#     """
#     #infinite loop of magical random numbers
#     print("Making random numbers")
#     while not thread_stop_event.isSet():
#         number = round(random()*10, 3)
#         print(number)
#         socketio.emit('newnumber', {'number': number}, namespace='/test')
#         socketio.sleep(5)

def facerec_cam1():
    r = redis.StrictRedis(host='0.0.0.0', port=6379, db=0, password='')
    face_cascade = cv2.CascadeClassifier("resources/haarcascade_frontalface_default.xml")
    ds_factor = 0.6

    """
    Generate a random number every 1 second and emit to a socketio instance (broadcast)
    Ideally to be run in a separate thread?
    """

    #infinite loop of magical random numbers
    print("Running face recognition cam1")

    while not thread_stop_event.isSet():
        people_camera1 = r.get('people_camera1')
        print('facerec_cam1: ' + str(people_camera1))

        socketio.emit('newnumber', {'people_name': str(people_camera1)}, namespace='/test')
        socketio.sleep(5)

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = socketio.start_background_task(facerec_cam1)

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

@app.route('/')
def index():
    # rendering webpage
    return render_template('index.html')

def gen():
    # video_capture = cv2.VideoCapture(0)
    # face_cascade = cv2.CascadeClassifier("resources/haarcascade_frontalface_default.xml")
    # ds_factor = 0.6

    # while True:
    #     # get camera frame
    #     success, image = video_capture.read()
    #
    #     image = cv2.resize(image, None, fx=ds_factor, fy=ds_factor, interpolation=cv2.INTER_AREA)
    #
    #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #     face_rects = face_cascade.detectMultiScale(gray, 1.3, 5)
    #     for (x, y, w, h) in face_rects:
    #         cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    #         break
    #     ret, jpeg = cv2.imencode('.jpg', image)
    #     jpeg_byte = jpeg.tobytes()
    #
    #     # socketio.emit('newnumber', {'number': 0.562}, namespace='/test')
    #
    #     # frame = camera.get_frame()
    #     yield (b'--frame\r\n'
    #            b'Content-Type: image/jpeg\r\n\r\n' + jpeg_byte + b'\r\n\r\n')
    r = redis.StrictRedis(host='0.0.0.0', port=6379, db=0, password='')

    while True:
        # get camera frame
        # frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + base64.b64decode(r.get('f_camera_0')) + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    # return Response(gen(),
    #                 mimetype='multipart/x-mixed-replace; boundary=frame')