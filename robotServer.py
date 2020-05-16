import socket
import time
import picamera

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 24
camera.vflip = True

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 4699))
server_socket.listen(0)

# Accept a single connection and make a file-like object out of it
vidStream = server_socket.accept()[0].makefile('wb')
cmdStream = server_socket.accept()[0].makefile('rb')
try:
    camera.start_recording(vidStream, format='h264')
    exitKey = False
    while not exitKey:
        cmd = input('enter e to exit: ')
        if cmd is 'e':
            exitKey = True
    camera.stop_recording()
finally:
    vidStream.close()
    server_socket.close()