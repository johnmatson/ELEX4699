import RPi.GPIO as GPIO
import time
import picamera
import socket
import asyncio
from KBHit import KBHit

class dcMotor:

    def __init__(self, IN1, IN2, PWM, PWMFREQ=10e3, PWMSLEEP=100e-6):
        # define pin numbering scheme
        GPIO.setmode(GPIO.BOARD)

        # setup motor pins
        GPIO.setup(IN1, GPIO.OUT)
        GPIO.setup(IN2, GPIO.OUT)
        GPIO.setup(PWM, GPIO.OUT)

        self.PWM = GPIO.PWM(PWM, PWMFREQ) # create PWM object
        self.PWM.start(0) # initialize PWM
        self.motor = (IN1,IN2,self.PWM) # create motor object

        self.PWMSLEEP = PWMSLEEP

    def fwd(self):
        GPIO.output(self.motor[0], GPIO.LOW)
        GPIO.output(self.motor[1], GPIO.HIGH)

    def rev(self):
        GPIO.output(self.motor[0], GPIO.HIGH)
        GPIO.output(self.motor[1], GPIO.LOW)

    def stop(self):
        GPIO.output(self.motor[0], GPIO.LOW)
        GPIO.output(self.motor[1], GPIO.LOW)

    async def inc(self, init=0, final=100):
        if init < final:
            for DC in range(final-init):
                self.motor[2].ChangeDutyCycle(init + DC)
                await asyncio.sleep(self.PWMSLEEP)

    async def dec(self, init=100, final=0):
        if init > final:
            for DC in range(init-final):
                self.motor[2].ChangeDutyCycle(init - DC)
                await asyncio.time.sleep(self.PWMSLEEP)


class servoMotor:

    def __init__(self, PWM, PWMFREQ=50, PWMSLEEP=100e-6):
        GPIO.setmode(GPIO.BOARD) # define pin numbering scheme
        GPIO.setup(PWM, GPIO.OUT) # setup servo pin

        self.PWM = GPIO.PWM(PWM, PWMFREQ) # create PWM object
        self.PWM.start(0) # initialize PWM

        self.PWMFREQ = PWMFREQ
        self.PWMSLEEP = PWMSLEEP

    def setPos(self, val): # val should be between 0 & 180
        # convert angle in degrees to duty cycle in pencentage for a 1-2ms pulse
        dutyCycle = self.PWMFREQ*(val+180)/1800
        self.PWM.ChangeDutyCycle(dutyCycle)

    def setPos1(self, val):
        self.PWM.ChangeDutyCycle(5)


class robotMotor:

    def __init__(self):
        # pins constants
        AIN1 = 11
        AIN2 = 13
        APWM = 15
        BIN1 = 29
        BIN2 = 31
        BPWM = 33
        SERVOPWM = 32

        # create motor objects
        self.left = dcMotor(AIN1, AIN2, APWM)
        self.right = dcMotor(BIN1, BIN2, BPWM)
        self.servo = servoMotor(SERVOPWM)

    async def fwd(self, driveTime=0.5, speed=100):
        self.left.fwd()
        self.right.fwd()
        self.left.inc(final=speed)
        self.right.inc(final=speed)
        await asyncio.sleep(driveTime)
        self.left.dec(init=speed)
        self.right.dec(init=speed)
        self.left.stop()
        self.right.stop()

    async def rev(self, driveTime=0.5, speed=100):
        self.left.rev()
        self.right.rev()
        self.left.inc(final=speed)
        self.right.inc(final=speed)
        await asyncio.sleep(driveTime)
        self.left.dec(init=speed)
        self.right.dec(init=speed)
        self.left.stop()
        self.right.stop()

    async def softLeft(self, driveTime=0.5, speed=100):
        self.left.fwd()
        self.right.fwd()
        self.right.inc(final=speed)
        time.sleep(driveTime)
        self.right.dec(init=speed)
        self.left.stop()
        self.right.stop()

    def softRight(self, driveTime=0.5, speed=100):
        self.left.fwd()
        self.right.fwd()
        self.left.inc(final=speed)
        await asyncio.sleep(driveTime)
        self.left.dec(init=speed)
        self.left.stop()
        self.right.stop()

    async def hardLeft(self, driveTime=0.5, speed=100):
        self.left.rev()
        self.right.fwd()
        self.left.inc(final=speed//2)
        self.right.inc(final=speed)
        await asyncio.sleep(driveTime)
        self.left.dec(init=speed//2)
        self.right.dec(init=speed)
        self.left.stop()
        self.right.stop()

    async def hardRight(self, driveTime=0.5, speed=100):
        self.left.fwd()
        self.right.rev()
        self.left.inc(final=speed)
        self.right.inc(final=speed//2)
        await asyncio.sleep(driveTime)
        self.left.dec(init=speed)
        self.right.dec(init=speed//2)
        self.left.stop()
        self.right.stop()

    def servoDown(self):
        self.servo.setPos(0)

    def servoUp(self):
        self.servo.setPos(90)


class camera:

    def __init__(self, local):
        camera = picamera.PiCamera()
        camera.resolution = (1296,972)
        camera.vflip = True
        camera.hflip = True
        if local:
            camera.start_preview(fullscreen=False, window=(100,200,400,600))


class server:

    def __init__(self):
        pass

    async def cmdRoutine(self, reader, writer):
        print('Command socket opened')
        while True:
            data = await reader.read(100)
            message = data.decode()

            print(f"Received {message!r}")

            if not data or message == 'e':
                break

        writer.close()
        print('Command socket closed')

    async def cmdServer(self):
        server = await asyncio.start_server(
            self.cmdRoutine, '0.0.0.0', 8888)

        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        async with server:
            await server.serve_forever()

    async def vidRoutine(self, reader, writer):
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

    async def vidServer(self):
        server = await asyncio.start_server(
            self.vidRoutine, '0.0.0.0', 7777)

        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        async with server:
            await server.serve_forever()



async def motorLoop():
    serverCmd = server()
    serverCmd.cmdServer()
    motor = robotMotor()

async def main():
    serverVid = server()
    await asyncio.gather(motorLoop(),serverVid.vidServer())

asyncio.run(main())




# class robot:

#     def start(self):
#         cmd = input('Run mode or test mode? (r/t): ')
#         if cmd == 'r':
#             cmd = input('Enable remote control? (y/n): ')
#             rc = False if cmd == 'n' else True
#             cmd = input('Enable local video? (y/n): ')
#             lv = False if cmd == 'n' else True
#             cmd = input('Enable remote video? (y/n): ')
#             rv = False if cmd == 'n' else True
#             cmd = input('Enable motors? (y/n): ')
#             mtr = False if cmd == 'n' else True
#             asyncio.run(self.main(rmtCtrl=rc, lclVid=lv, rmtVid=rv, mtrs=mtr))
#         elif cmd == 't':
#             print('Test mode not yet funcitonal')
#             self.start()


#     async def main(self, rmtCtrl=True, lclVid=True, rmtVid=True, mtrs=True):

#         # network setup
#         if rmtCtrl or rmtVid:
#             self.server = server()
#             print('Server established')
#         if rmtCtrl:
#             print('Waiting for control client...')
#             # server.connect???
#             print('Connected to control client')
#         if rmtVid:
#             print('Waiting for video client...')
#             # server.connect???
#             print('Connected to video client')

#         # peripherals setup
#         if mtrs:
#             self.motor = robotMotor()
#             print('Motors ready')
#         if lclVid or rmtVid:
#             self.camera = camera(lclVid)
#             print('Video ready')

#         # event loop
        






# camera = picamera.PiCamera()
# camera.resolution = (1296,972)
# camera.vflip = True
# camera.hflip = True
# camera.start_preview(fullscreen=False, window=(100,200,400,600))

# server_socket = socket.socket()
# server_socket.bind(('0.0.0.0', 9964))
# server_socket.listen(0)
# print('waiting for connection')
# connection, addr = server_socket.accept()
# print('connected to {}',addr)

# motorControl = robotMotor()
# exitKey = False
# while exitKey is False:

#     data = connection.recv(1024)
#     keyCmd = data.decode('utf-8')
#     if not data:
#         break
#     # keyCmd = input()
#     if keyCmd is 'e':
#         exitKey = True
#     elif keyCmd is '5':
#         motorControl.fwd()
#     elif keyCmd is '2':
#         motorControl.rev()
#     elif keyCmd is '1':
#         motorControl.softLeft()
#     elif keyCmd is '4':
#         motorControl.hardLeft()
#     elif keyCmd is '3':
#         motorControl.softRight()
#     elif keyCmd is '6':
#         motorControl.hardRight()
#     elif keyCmd is '+':
#         motorControl.servoDown()
#     elif keyCmd is '-':
#         motorControl.servoUp()

# connection.close()
# server_socket.close()
# camera.stop_preview()
# GPIO.cleanup()