import io
import socket
import struct
import time
import threading
import picamera


class AdeeptAWR():
    """ Parent Class for Robot """

    # Create initial sockets and threaded connection lock

    command_sock = socket.socket()
    command_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    command_sock.bind(('0.0.0.0', 10617))
    command_sock.listen(0)
    command_stream = None

    status_sock = socket.socket()
    video_sock = socket.socket()
    video_file = None

    def wait_for_client_connection(self):
        """ Target function to thread socket connections """
        self.command_stream, self.client = self.command_sock.accept()
        print("Command socket connected to: ", self.client)
        self.status_sock.connect((self.client[0], 10618))
        self.video_sock.connect((self.client[0], 10619))
        self.video_file = self.video_sock.makefile('wb')
    client = None

    def start_connections(self):
        """ Threading function to establish client connections """
        print("Starting connection threading...")
        client_connection_threading = \
            threading.Thread(target=self.wait_for_client_connection,
                             daemon=True)
        client_connection_threading.start()

    start_timer = None
    end_timer = None

    def start_camera(self):
        """ Setter method to start video stream """
        print("Starting video threading...")
        self.start_timer = time.time()
        self.camera.start_recording(self, format='mjpeg')

    def stop_camera(self):
        """ Setter method to stop video stream """
        print("Stopping camera......")
        self.camera.stop_recording()
        self.end_timer = time.time()
        print('Sent %d images in %d seconds at %.2ffps' %
              (self.count, self.end_timer-self.start_timer,
               self.count /
               (self.end_timer-self.start_timer)))

    stream = io.BytesIO()
    count = 0

    def write(self, buf):
        """
        Custom write method used by camera.start_recording() to split mjpeg
        frames and send to socket fiel.

        Writes recording buffer to BytesIO stream until jpg magic bytes are
        found. Then writes the size and stream contents to the socket file.

        Increments counter for FPS calculations.

        """
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
                print("Writing frame # ", self.count)
                self.stream.seek(0)
        self.stream.write(buf)

    def __init__(self, resolution=(1280, 720), framerate=30):

        self.camera = picamera.PiCamera(resolution=resolution,
                                        framerate=framerate)
        self.start_connections()



# TODO Wireless hotspot

# TODO Stream connection

# TODO Led object

# TODO Motor object

# TODO Speaker object

if __name__ == "__main__":
    robot = AdeeptAWR(framerate=49)
    if not robot.client:
        print("No client connected", end=" ", flush=True)
        while not robot.client:
            print(".", end=" ", flush=True)
            time.sleep(1)
    robot.start_camera()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Quitting")
        robot.stop_camera()
