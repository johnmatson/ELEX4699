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

async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")

    print(f"Send: {message!r}")
    writer.write(data)
    await writer.drain()

    print("Close the connection")
    writer.close()

async def main():
    server = await asyncio.start_server(
        handle_echo, '0.0.0.0', 8888)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())