# import socket
# import subprocess

# # Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# # all interfaces)
# server_socket = socket.socket()
# server_socket.bind(('0.0.0.0', 8000))
# server_socket.listen(0)

# # Accept a single connection and make a file-like object out of it
# connection = server_socket.accept()[0].makefile('rb')
# # try:
# # Run a viewer with an appropriate command line. Uncomment the mplayer
# # version if you would prefer to use mplayer instead of VLC
# cmdline = ['/Applications/VLC.app/Contents/MacOS/VLC', '--demux', 'h264', '-']
# #cmdline = ['mplayer', '-fps', '25', '-cache', '1024', '-']
# player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
# while True:
#     # Repeatedly read 1k of data from the connection and write it to
#     # the media player's stdin
#     data = connection.read(1024)
#     if not data:
#         break
#     player.stdin.write(data)
# # finally:
# connection.close()
# server_socket.close()
# player.terminate()


import socket
import time
import picamera

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 24

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('wb')
try:
    camera.start_recording(connection, format='h264')
    camera.wait_recording(60)
    camera.stop_recording()
finally:
    connection.close()
    server_socket.close()