import socket
import subprocess

# Connect a client socket to my_server:8000 (change my_server to the
# hostname of your server)
client_socket = socket.socket()
client_socket.connect(('192.168.0.27', 4699))

# Make a file-like object out of the connection
vidStream = client_socket.makefile('rb')
# cmdStream = client_socket.makefile('wb')
try:
    # Run a viewer with an appropriate command line
    cmdline = ['/Applications/VLC.app/Contents/MacOS/VLC', '--demux', 'h264', '-']
    player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
    data = ' '
    while data:
        # Repeatedly read 1k of data from the connection and write it to
        # the media player's stdin
        data = vidStream.read(1024)
        player.stdin.write(data)
finally:
    vidStream.close()
    client_socket.close()
    player.terminate()