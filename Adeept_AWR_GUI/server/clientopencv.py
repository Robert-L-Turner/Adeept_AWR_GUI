import io
import socket
import struct
import numpy
import cv2

# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces)
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)
# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('rb')

colorUpper = numpy.array([2, 12, 24])
colorLower = numpy.array([0, 3, 6])
font = cv2.FONT_HERSHEY_SIMPLEX

try:
    while True:
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            break
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO(connection.read(image_len))
        img = cv2.imdecode(numpy.fromstring(image_stream.read(), numpy.uint8), 1)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) #Convert captured images to HSV color space
        mask = cv2.inRange(hsv, colorLower, colorUpper) #Traverse the colors in the target color range in the HSV color space, and turn these color blocks into masks
        mask = cv2.erode(mask, None, iterations=2) #Corrosion of small pieces of mask (noise) in the picture becomes small (small pieces of color or noise disappear)
        mask = cv2.dilate(mask, None, iterations=2) #Inflate, and resize the large mask that was reduced in the previous step to its original size
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)[-2]
        #Find a few masks in the picture
        center = None
        if len(cnts) > 0:
        #If the number of whole masks in the picture is greater than one
        #Find the coordinates of the center point of the object of the target color and the size of the object in the picture
            c = max(cnts, key=cv2.contourArea)
            ((box_x, box_y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            X = int(box_x)
            Y = int(box_y)
            # Get the center point coordinates of the target color object and output
            print('Target color object detected')
            print('X:%d'%X)
            print('Y:%d'%Y)
            print('-------')
            # Write text on the screen:Target Detected
            cv2.putText(img,'Target Detected',(40,60), font, 0.5,(255,255,255),1,cv2.LINE_AA)
            # Draw a frame around the target color object
            cv2.rectangle(img,(int(box_x-radius),int(box_y+radius)),(int(box_x+radius),int(box_y-radius)),(255,255,255),1)
        else:
            cv2.putText(img,'Target Detecting',(40,60), font, 0.5,(255,255,255),1,cv2.LINE_AA)
            print('No target color object detected')

        cv2.imshow("img", img)
        cv2.waitKey(1)
finally:
    cv2.destroyAllWindows()
    connection.close()
    server_socket.close()
