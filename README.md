## Smart Mobility - Face Recognition server

- Flask REST Framework
- Streaming video that processing face recognition
- Send the message that face that recognize via socket.io for using in frontend framework

# Getting Started

Download and Install python3, if you don't have them.

### Installing

Install python library `face_recognition`
- https://github.com/ageitgey/face_recognition

Install python environment

**conda** 

```
conda env create -f environment.yml
conda activate facerec
```

or

**pip**

```
pip3 install -r requirements.txt
```

### Usage

**Start web server**

Start flask server by run following commands in terminal

```
python3 server.py
```

**Start web application**

Go to this demo for usage. [Web Application](https://github.com/kritnambutt/FaceRecognition_web/)

## Result

For Flask Server go to (http://localhost:5000)

For Video Streaming go to (http://localhost:5000/video_feed)

## License
This project is licensed under the MIT License


