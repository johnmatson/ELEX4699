# import socket
# import subprocess

# # Connect a client socket to my_server:8000 (change my_server to the
# # hostname of your server)
# client_socket = socket.socket()
# client_socket.connect(('192.168.0.27', 4699))

# # Make a file-like object out of the connection
# vidStream = client_socket.makefile('rb')
# # cmdStream = client_socket.makefile('wb')
# try:
#     # Run a viewer with an appropriate command line
#     cmdline = ['/Applications/VLC.app/Contents/MacOS/VLC', '--demux', 'h264', '-']
#     player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
#     data = ' '
#     while data:
#         # Repeatedly read 1k of data from the connection and write it to
#         # the media player's stdin
#         data = vidStream.read(1024)
#         player.stdin.write(data)
# finally:
#     vidStream.close()
#     client_socket.close()
#     player.terminate()


import asyncio
import subprocess
from KBHit import KBHit

async def cmdClient():
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)
        # '192.168.0.27', 8888)

    kb = KBHit()
    while True:
        if kb.kbhit():
            message = kb.getch()
            print(f'Send: {message!r}')
            writer.write(message.encode())
            if message == 'e':
                break
        await asyncio.sleep(0)

    writer.close()
    print('Command connection closed')


async def vidClient():
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 7777)
        # '192.168.0.27', 8888)

    try:
        # Run a viewer with an appropriate command line
        cmdline = ['/Applications/VLC.app/Contents/MacOS/VLC', '--demux', 'h264', '-']
        player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
        while True:
            data = await reader.read(100)
            player.stdin.write(data)
            if not data:
                break
                
    finally:
        writer.close()
        player.terminate()
        print('Video connection closed')


async def main():
    await asyncio.gather(cmdClient(), vidClient())

asyncio.run(main())