# import socket
# import time
# import picamera

# camera = picamera.PiCamera()
# camera.resolution = (640, 480)
# camera.framerate = 24
# camera.vflip = True
# camera.hflip = True

# server_socket = socket.socket()
# server_socket.bind(('0.0.0.0', 4699))
# server_socket.listen(0)

# # Accept a single connection and make a file-like object out of it
# vidStream = server_socket.accept()[0].makefile('wb')
# # cmdStream = server_socket.accept()[0].makefile('rb')
# try:
#     camera.start_recording(vidStream, format='h264')
#     exitKey = False
#     while not exitKey:
#         cmd = input('enter e to exit: ')
#         if cmd is 'e':
#             exitKey = True
#     camera.stop_recording()
# finally:
#     vidStream.close()
#     server_socket.close()


import asyncio
import picamera

async def cmdRoutine(reader, writer):
    print('Command socket opened')
    while True:
        data = await reader.read(100)
        message = data.decode()

        print(f"Received {message!r}")

        if not data or message == 'e':
            break

    writer.close()
    print('Command socket closed')

async def cmdServer():
    server = await asyncio.start_server(
        cmdRoutine, '0.0.0.0', 8888)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

async def vidRoutine(reader, writer):
    print('Video socket opened')

    camera = picamera.PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 24
    camera.vflip = True
    camera.hflip = True

    try:
        camera.start_recording(writer, format='h264')
        while True:
            data = await reader.read(100)
            if not data:
                break
    finally:
        camera.stop_recording()
        writer.close()
        print('Video socket closed')

async def vidServer():
    server = await asyncio.start_server(
        vidRoutine, '0.0.0.0', 7777)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

async def main():
    await asyncio.gather(cmdServer(),vidServer())


asyncio.run(main())