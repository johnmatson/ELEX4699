'''
A Python script to remotely control the Raspberry Pi robot.

Current functionality includes local and remote motor control
using a num-pad. Program also streams video over the network
to the remote client. To control the robot remotely, run
robot.py on the Raspberry Pi, then run robotClient.py on the
remote device of choice.

Robot controls are as follows:
1: soft left
2: reverse
3: soft right
4: hard left
5: forward
6: hard right
+: servo up
-: servo down

Code is implemented using the asyncio library to allow for
simultaneous mutiple socket connections and motor control.
All blocking functions should be called using await.

Be aware that currently servo controls are not functioning
properly. Also, as of yet, the robot only opperates in
manual mode. Autonomous mode may be added in a future
release.

Written by John Matson in spring 2020 for BCIT's ELEX 4699,
taught by Craig Hennesey.
'''

import asyncio
import subprocess
from KBHit import KBHit

async def cmdClient():
    '''
    Opens connection with command server using asyncio's
    stream APIs. Connects to Raspberry Pi at 192.168.0.27
    on port 8888. Reads keyboard input and transmits to
    server.
    '''

    reader, writer = await asyncio.open_connection(
        '192.168.0.27', 8888)

    kb = KBHit()
    while True:
        if kb.kbhit():
            message = kb.getch()
            print(f'Send: {message!r}')
            writer.write(message.encode())

            data = await reader.read(100)
            if not data:
                break
        await asyncio.sleep(0)

    writer.close()
    print('Command connection closed')

async def vidClient():
    '''
    Opens connection with video server using asyncio's
    stream APIs. Connects to Raspberry Pi at 192.168.0.27
    on port 7777. Decodes and transfers video stream data
    to VLC video player.
    '''

    reader, writer = await asyncio.open_connection(
        '192.168.0.27', 7777)

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