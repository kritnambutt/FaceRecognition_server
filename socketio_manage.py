from server import socketio

class socketio_manage:
    def __init__(self):
        socketio.emit('message', 'message test')
