import io
import socket
import struct
import time
import threading
import picamera


# TODO Robot Class
class AdeeptAWR():
    def __init__(self):
        self.connections = SocketConnections
        self.camera = picamera.PiCamera(resolution=(1280, 720), framerate=49)
        self.camera_on = False

    def __exit__(self):
        self.camera.close()

# TODO Camera object

    def video_streaming(self):
        self.video_output = SplitFrames(self.connections.video_file)
        self.camera.start_recording(self.video_output, format='mjpeg')
        while self.camera_on:
            continue 
        self.camera.stop_recording()
        self.connections.video_stream.write(struct.pack('<L', 0))

    def start_camera(self):
        self.camera_on = True

        self.video_stream_threading = threading.Thread(target=self.video_streaming)
        self.video_stream_threading.setDaemon(True)
        self.video_stream_threading.start()

    def stop_camera(self):
        self.camera_on = False

class SplitFrames(video_file):
    def __init__(self, ):
        self.video_file = video_file
        self.stream = io.BytesIO()
        self.count = 0

        def write(self, buf):
            if buf.startswith(b'\xff\xd8'):
                # Start of new frame; send the old one's length
                # then the data
                size = self.stream.tell()
                if size > 0:
                    self.video_file.write(struct.pack('<L', size))
                    self.video_file.flush()
                    self.stream.seek(0)
                    self.video_file.write(self.stream.read(size))
                    self.count += 1
                    self.stream.seek(0)
            self.stream.write(buf)


# TODO Wireless hotspot

# TODO Stream connection
class SocketConnections():
    def __init__(self):
        self.command_sock = socket.socket()
        self.command_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.command_sock.bind(('0.0.0.0', 10617))

        self.status_stream = socket.socket()
        self.video_stream = socket.socket()

        def wait_for_client_connection(self):
            self.command_sock.listen(0)
            self.connection, self.client = self.command_sock.accept()
            self.status_stream.connect(self.client[0], 10618)
            self.video_stream.connect(self.client[0], 10619)
            self.video_file = self.video_stream.makefile('wb')

        self.client_connection_threading = \
            threading.Thread(target=wait_for_client_connection)
        self.client_connection_threading.setDaemon(True)
        self.client_connection_threading.start()


# TODO Led object

# TODO Motor object

# TODO Speaker object
