# from streamer import streamer
import cv2
import face_recognition
import numpy as np
import redis
import base64

# face_cascade = cv2.CascadeClassifier("resources/haarcascade_frontalface_default.xml")
# ds_factor = 0.6

class VideoCamera2():
    def __init__(self):
        # Get a reference to webcam #0 (the default one)
        self.video_capture = cv2.VideoCapture('rtsp://admin:HuaWei123@172.17.2.202/LiveMedia/ch1/Media1')
        self.r = redis.StrictRedis(host='0.0.0.0', port=6379, db=0, password='')

        # Load a sample picture and learn how to recognize it.
        obama_image = face_recognition.load_image_file("obama.jpg")
        obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

        # Load a second sample picture and learn how to recognize it.
        yo_image = face_recognition.load_image_file("yo.jpg")
        yo_face_encoding = face_recognition.face_encodings(yo_image)[0]

        # Load a second sample picture and learn how to recognize it.
        yok_image = face_recognition.load_image_file("yok.jpg")
        yok_face_encoding = face_recognition.face_encodings(yok_image)[0]

        # Create arrays of known face encodings and their names
        self.known_face_encodings = [
            obama_face_encoding,
            yo_face_encoding,
            yok_face_encoding,
        ]
        self.known_face_names = [
            "Barack Obama",
            "Yo",
            "Yok"
        ]

        # Initialize some variables
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True

    def __del__(self):
        self.video_capture.release()

    def broadcast(self, frame, quality=85):
        """
        compress cv2 frame to jpg string and send to redis server
        Args:
            frame: cv2 frame
            quality: compression percentage
        """
        encode = [cv2.IMWRITE_JPEG_QUALITY, quality]
        ret, buffer = cv2.imencode('.jpg', frame, encode)
        buffer = buffer.tobytes()
        content = base64.b64encode(buffer)
        self.r.setex('f_camera_1', 1, content)

    def broadcast_pil(self, image, quality=85):
        """
        broadcast pillow image
        """
        frame = np.array(image)
        self.broadcast(frame, quality)

    def get_frame(self):
            success, frame = self.video_capture.read()

            # image = cv2.resize(image, None, fx=ds_factor, fy=ds_factor, interpolation=cv2.INTER_AREA)
            #
            # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # face_rects = face_cascade.detectMultiScale(gray, 1.3, 5)
            # for (x, y, w, h) in face_rects:
            #     cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            #     break
            # ret, jpeg = cv2.imencode('.jpg', image)
            # return jpeg.tobytes()

            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
            if self.process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

                self.face_names = []
                for face_encoding in self.face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"

                    # # If a match was found in known_face_encodings, just use the first one.
                    # if True in matches:
                    #     first_match_index = matches.index(True)
                    #     name = known_face_names[first_match_index]

                    # Or instead, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]

                    self.face_names.append(name)

            self.process_this_frame = not self.process_this_frame

            # Display the results
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            # Display the resulting image
            # self.broadcast(frame, quality=70)
            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()

# instance = VideoCamera2()
# instance.get_frame()