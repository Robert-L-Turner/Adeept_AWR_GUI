import socket
import numpy
import cv2
import struct
import io
import threading
import time
from queue import Queue


class AdeeptAWRController(object):

    status_socket = socket.socket()
    status_socket.setsockopt(socket.SOL_SOCKET,
                             socket.SO_REUSEADDR, 1)
    status_socket.bind(('0.0.0.0', 10618))
    status_socket.listen(0)
    status_stream = None

    video_socket = socket.socket()
    video_socket.setsockopt(socket.SOL_SOCKET,
                            socket.SO_REUSEADDR, 1)
    video_socket.bind(('0.0.0.0', 10619))
    video_socket.listen(0)
    video_stream = None
    video_file = None

    command_socket = socket.socket()

    def wait_for_connection(self):
        self.command_socket.connect(('192.168.0.234', 10617))
        print("command socket connected")

        self.video_stream, _ = self.video_socket.accept()
        self.video_file = self.video_stream.makefile('rb')
        print("video_stream connection established")

        self.status_stream, _ = self.status_socket.accept()
        print("status_stream connection established")

    def start_connections(self):
        print("Starting connection threading...")
        client_connection_threading = \
            threading.Thread(target=self.wait_for_connection,
                             daemon=True)
        client_connection_threading.start()

    class Stream(object):
        stream_queue = Queue()

        def __init__(self, video_file):
            self.video_file = video_file
            print(self.video_file)
            self.image = None

            self.frame_count = 0
            self.colorUpper = numpy.array([2, 12, 24])
            self.colorLower = numpy.array([0, 3, 6])
            self.font = cv2.FONT_HERSHEY_SIMPLEX

            self.color_found = False
            self.box_x = None
            self.box_y = None
            self.radius = None

            self.find_color = False

        def opencv_find_color(self):
            # Convert captured images to HSV color space
            hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
            # Traverse the colors in the target color range in the HSV color space,
            # and turn these color blocks into masks
            mask = cv2.inRange(hsv, self.colorLower, self.colorUpper)
            # Corrosion of small pieces of mask (noise) in the picture becomes
            # small (small pieces of color or noise disappear)
            mask = cv2.erode(mask, None, iterations=2)
            # Inflate, and resize the large mask that was reduced in the previous
            # step to its original size
            mask = cv2.dilate(mask, None, iterations=2)
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)[-2]
            # Find a few masks in the picture
            if len(cnts) > 0:
                # If the number of whole masks in the picture is greater than one
                # Find the coordinates of the center point of the object of the
                # target color and the size of the object in the picture
                self.color_found = True
                c = max(cnts, key=cv2.contourArea)
                ((self.box_x, self.box_y), self.radius) = cv2.minEnclosingCircle(c)

        def video_stream(self):
            print("Starting video stream...")
            while True:
                self.image_len = struct.unpack('<L',
                                               self.video_file.read
                                               (struct.calcsize('<L')))[0]
                self.image_stream = io.BytesIO(self.video_file.read
                                               (self.image_len))
                self.image = cv2.imdecode(numpy.frombuffer(
                    self.image_stream.read(), numpy.uint8), 1)
                self.frame_count += 1
                self.stream_queue.put(self.image)
                #cv2.imshow("Stream", self.image)
                #cv2.waitKey(1)

        def start_video_stream(self):
            print("Starting video thread...")
            self.start_timer = time.time()
            video_stream_threading = \
                threading.Thread(target=self.video_stream, daemon=True)
            video_stream_threading.start()

        def stop_video_stream(self):
            self.end_timer = time.time()
            print('Sent %d images in %d seconds at %.2ffps' %
                  (self.frame_count, self.end_timer-self.start_timer,
                   self.frame_count/(self.end_timer-self.start_timer)))

    def __init__(self):
        self.start_connections()
        while self.video_stream is None:
            pass
        self.stream = self.Stream(self.video_file)
        self.stream.start_video_stream()


# TODO Video Streaming

# TODO Drive controls

# TODO Light slider

# TODO Status Bar

# TODO Mode Selection

if __name__ == "__main__":
    gui = AdeeptAWRController()
    try:
        while True:
            frame = gui.stream.stream_queue.get()
            cv2.imshow("Frame", frame)
            cv2.waitKey(1)
    except KeyboardInterrupt:
        gui.stream.stop_video_stream()
        gui.video_stream.close()
        gui.status_stream.close()
