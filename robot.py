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
                await asyncio.sleep(self.PWMSLEEP)


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
        await self.left.inc(final=speed)
        await self.right.inc(final=speed)
        await asyncio.sleep(driveTime)
        await self.left.dec(init=speed)
        await self.right.dec(init=speed)
        self.left.stop()
        self.right.stop()

    async def rev(self, driveTime=0.5, speed=100):
        self.left.rev()
        self.right.rev()
        await self.left.inc(final=speed)
        await self.right.inc(final=speed)
        await asyncio.sleep(driveTime)
        await self.left.dec(init=speed)
        await self.right.dec(init=speed)
        self.left.stop()
        self.right.stop()

    async def softLeft(self, driveTime=0.5, speed=100):
        self.left.fwd()
        self.right.fwd()
        await self.right.inc(final=speed)
        await asyncio.sleep(driveTime)
        await self.right.dec(init=speed)
        self.left.stop()
        self.right.stop()

    async def softRight(self, driveTime=0.5, speed=100):
        self.left.fwd()
        self.right.fwd()
        await self.left.inc(final=speed)
        await asyncio.sleep(driveTime)
        await self.left.dec(init=speed)
        self.left.stop()
        self.right.stop()

    async def hardLeft(self, driveTime=0.5, speed=100):
        self.left.rev()
        self.right.fwd()
        await self.left.inc(final=speed//2)
        await self.right.inc(final=speed)
        await asyncio.sleep(driveTime)
        await self.left.dec(init=speed//2)
        await self.right.dec(init=speed)
        self.left.stop()
        self.right.stop()

    async def hardRight(self, driveTime=0.5, speed=100):
        self.left.fwd()
        self.right.rev()
        await self.left.inc(final=speed)
        await self.right.inc(final=speed//2)
        await asyncio.sleep(driveTime)
        await self.left.dec(init=speed)
        await self.right.dec(init=speed//2)
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

    async def cmdRoutine(self, reader, writer, commands):
        print('Command socket opened')
        while True:
            data = await reader.read(100)
            command = data.decode()
            if command:
                commands.append(command)
            if not data:
                break
        writer.close()
        print('Command socket closed')

    async def cmdServer(self, commands):
        server = await asyncio.start_server(
            lambda reader, writer: self.cmdRoutine(reader, writer, commands), '0.0.0.0', 8888)

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



async def control(cmds):
    motor = robotMotor()
    kb = KBHit()
    local = True
    localDict = {True:'local', False:'remote'}

    while True:
        await asyncio.sleep(0)
        cmd = ''
        if kb.kbhit():
            cmd = kb.getch()
            local = True
        elif cmds:
            cmd = cmds[-1]
            cmds.clear()
            local = False

        if cmd == 'e':
            break
        elif cmd is '5':
            await motor.fwd()
            print(localDict[local],'- foward')
        elif cmd is '2':
            await motor.rev()
            print(localDict[local],'- reverse')
        elif cmd is '1':
            await motor.softLeft()
            print(localDict[local],'- soft left')
        elif cmd is '4':
            await motor.hardLeft()
            print(localDict[local],'- hard left')
        elif cmd is '3':
            await motor.softRight()
            print(localDict[local],'- soft right')
        elif cmd is '6':
            await motor.hardRight()
            print(localDict[local],'- hard right')
        elif cmd is '+':
            motor.servoDown()
        elif cmd is '-':
            motor.servoUp()


async def main():
    cmds = []
    cmdsvr = server()
    vidsvr = server()
    await asyncio.gather(control(cmds),cmdsvr.cmdServer(cmds),vidsvr.vidServer())

try:
    asyncio.run(main())
finally:
    GPIO.cleanup()