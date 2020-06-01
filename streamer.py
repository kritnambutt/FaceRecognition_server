import redis
import base64
import numpy as np
import cv2


class streamer:
    """
    Stream helper
    """

    def __init__(self, host='0.0.0.0', port=6379):
        self.r = redis.StrictRedis(host=host, port=port, db=0, password='')

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
        self.r.setex('frame', 1, content)

    def broadcast_pil(self, image, quality=85):
        """
        broadcast pillow image
        """
        frame = np.array(image)
        self.broadcast(frame, quality)
