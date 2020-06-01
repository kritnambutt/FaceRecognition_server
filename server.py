# server.py

# import the necessary packages
from flask import Flask, render_template, Response
from flask_socketio import SocketIO, send, emit
# from socketio_manage import *
# from camera1 import VideoCamera1
# from camera2 import VideoCamera2
import json
import threading
import face_recognition
import cv2
import numpy as np
import redis
import base64
from random import random
from time import sleep
from threading import Thread, Event

# Configuration app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True
#turn the flask app into a socketio app
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=None, logger=True, engineio_logger=True) # CORS
# socketio = SocketIO(app)

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

def randomNumberGenerator():
    """
    Generate a random number every 1 second and emit to a socketio instance (broadcast)
    Ideally to be run in a separate thread?
    """
    #infinite loop of magical random numbers
    print("Making random numbers")
    while not thread_stop_event.isSet():
        number = round(random()*10, 3)
        print(number)
        socketio.emit('newnumber', {'number': number}, namespace='/test')
        socketio.sleep(5)

# Receive the message from clients defines event handlers using the socketio.on decorator.
@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = socketio.start_background_task(randomNumberGenerator)

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


@app.route('/')
def index():
    # rendering webpage
    return render_template('index.html')

def find_camera(id):
    cameras = [{
        'camera_id': '0',
        'camera_name': 'webcam',
        'frame_name': 'f_camera_0'
    },{
        'camera_id': '1',
        'camera_name': 'front_AILAB_BKD',
        'frame_name': 'f_camera_1'
    }]

    camera_exist = list(filter(lambda x:x["camera_id"]==id,cameras))
    if len(camera_exist) > 0:
        camera_frame = camera_exist[0]['frame_name']
        return camera_frame
        # return camera_class
    else:
        return None
    # return (list(filter(lambda x:x["camera_id"]==id,cameras)))
    #  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
    #  for webcam use zero(0)

def gen(frame_camera):
    r = redis.StrictRedis(host='0.0.0.0', port=6379, db=0, password='')

    while True:
        # get camera frame
        # frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + base64.b64decode(r.get(frame_camera)) + b'\r\n\r\n')

    # # yield the output frame in the byte format
    # yield (b'--frame\r\n'
    #        b'Content-Type: image/jpeg\r\n\r\n' + jpeg_bytes + b'\r\n\r\n')


# @app.route('/video_feed')
# def video_feed():
#     return Response(gen(VideoCamera1()),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')
#     # return Response(gen(),
#     #                 mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed/<string:id>/', methods=["GET"])
def video_feed(id):
    camera_frame_name = find_camera(id)

    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(camera_frame_name),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # defining server ip address and port
    socketio.run(app, host='127.0.0.1', debug=True)
    # app.run(host='127.0.0.1', port='5000', debug=True)