import socket
import numpy
import cv2
import struct
import io
import threading


class AdeeptAWRController(object):
    def __init__(self):
        self.connections = SocketConnections()
        self.stream = Stream(self.connections.video_file)
        self.stream.start_find_color()
        self.stream.start_video_stream()


class SocketConnections(object):
    def __init__(self):
        self.status_socket = socket.socket()
        self.status_socket.bind(('0.0.0.0', 10619))
        self.status_socket.listen(0)

        self.video_socket = socket.socket()
        self.video_socket.bind(('0.0.0.0', 10618))
        self.video_socket.listen(0)

        command_socket = socket.socket()
        command_socket.connect(('192.168.0.234', 10617))

        self.video_stream, _ = self.video_socket.accept()
        self.video_file = self.video_stream.makefile('rb')

        self.status_stream, _ = self.status_socket.accept()


class Stream(object):
    def __init__(self, video_file):
        self.video_file = video_file
        self.image = None

        self.frame_count = 0
        self.colorUpper = numpy.array([2, 12, 24])
        self.colorLower = numpy.array([0, 3, 6])
        self.font = cv2.FONT_HERSHEY_SIMPLEX

        self.color_found = True
        self.box_x = None
        self.box_y = None
        self.radius = None

        self.video_stream_on = True
        self.find_color = True
 
    def opencv_find_color(self):
        # Convert captured images to HSV color space
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        # Traverse the colors in the target color range in the HSV color space, and turn these color blocks into masks
        mask = cv2.inRange(hsv, self.colorLower, self.colorUpper)
        # Corrosion of small pieces of mask (noise) in the picture becomes small (small pieces of color or noise disappear)
        mask = cv2.erode(mask, None, iterations=2)
        # Inflate, and resize the large mask that was reduced in the previous step to its original size
        mask = cv2.dilate(mask, None, iterations=2)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]
        # Find a few masks in the picture
        center = None
        if len(cnts) > 0:
            # If the number of whole masks in the picture is greater than one
            # Find the coordinates of the center point of the object of the target color and the size of the object in the picture
            self.color_found = True
            c = max(cnts, key=cv2.contourArea)
            ((self.box_x, self.box_y), self.radius) = cv2.minEnclosingCircle(c)

    def video_stream(self):
        while self.video_stream_on:
            self.image_len = struct.unpack('<L', self.video_file.read(struct.calcsize('<L')))[0]
            self.image_stream = io.BytesIO(self.video_file.read(self.image_len))
            self.image = cv2.imdecode(numpy.fromstring(self.image_stream.read(), numpy.uint8), 1)
            if self.frame_count == 30 & self.find_color:
                self.opencv_find_color()
                self.frame_count = 0
            if self.color_found:
                # Write text on the screen:Target Detected
                cv2.putText(self.image, 'Target Detected', (40, 60), self.font,
                            0.5, (255, 255, 255), 1, cv2.LINE_AA)
                # Draw a frame around the target color object
                cv2.rectangle(self.image, (int(self.box_x-self.radius),
                                           int(self.box_y+self.radius)),
                              (int(self.box_x+self.radius),
                               int(self.box_y-self.radius)),
                              (255, 255, 255), 1)
            else:
                cv2.putText(self.image, 'Target Detecting', (40, 60),
                            self.font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            self.frame_count += 1
            cv2.imshow("Stream", self.image)
            cv2.waitKey(1)

    def start_find_color(self):
        self.find_color = True

    def stop_find_color(self):
        self.find_color = False

    def start_video_stream(self):
        self.video_stream_on = True
        self.video_stream_threading = \
            threading.Thread(target=self.video_stream)
        self.video_stream_threading.setDaemon(False)
        self.video_stream_threading.start()

    def stop_video_stream(self):
        self.video_stream_on = False


# TODO Video Streaming

# TODO Drive controls

# TODO Light slider

# TODO Status Bar

# TODO Mode Selection
