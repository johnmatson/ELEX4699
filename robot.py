'''
A Python script to operate a remote controlled robot on the
Raspberry Pi.

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

import RPi.GPIO as GPIO
import time
import picamera
import socket
import asyncio
from KBHit import KBHit


class dcMotor:
    '''
    Contorl DC motors with the TB6612FNG dual-channel H-bridge and
    Raspberry Pi GPIO.
    '''

    def __init__(self, IN1, IN2, PWM, PWMFREQ=10e3, PWMSLEEP=100e-6):
        '''
        IN1, IN2 and PWM are H-bridge pin labels. These parameters take
        the corresponding GPIO pin numbers (board numbering scheme) as
        connected. The PWMFREQ parameter takes the pulse-width-modulation
        frequency, and the PWMSLEEEP parameter takes the time between
        each 1% PWM step; a non-zero PWMSLEEP time decreases the
        likelihood of current spikes.
        '''

        # define pin numbering scheme
        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(IN1, GPIO.OUT)
        GPIO.setup(IN2, GPIO.OUT)
        GPIO.setup(PWM, GPIO.OUT)

        self.PWM = GPIO.PWM(PWM, PWMFREQ)
        self.PWM.start(0)
        self.motor = (IN1,IN2,self.PWM)

        self.PWMSLEEP = PWMSLEEP

    def fwd(self):
        ''' Configures the motor to run forward.
        '''

        GPIO.output(self.motor[0], GPIO.LOW)
        GPIO.output(self.motor[1], GPIO.HIGH)

    def rev(self):
        ''' Configures the motor to run in reverse.
        '''
        
        GPIO.output(self.motor[0], GPIO.HIGH)
        GPIO.output(self.motor[1], GPIO.LOW)

    def stop(self):
        ''' Configures the motor to stop.
        '''

        GPIO.output(self.motor[0], GPIO.LOW)
        GPIO.output(self.motor[1], GPIO.LOW)

    async def inc(self, init=0, final=100):
        '''
        Ramps the motor PWM value up from init parameter value
        to final parameter value in 1% steps every PWMSLEEP
        seconds. 
        '''

        if init < final:
            for DC in range(final-init):
                self.motor[2].ChangeDutyCycle(init + DC)
                await asyncio.sleep(self.PWMSLEEP)

    async def dec(self, init=100, final=0):
        '''
        Ramps the motor PWM value down from init parameter
        value to final parameter value in 1% steps every
        PWMSLEEP seconds. 
        '''

        if init > final:
            for DC in range(init-final):
                self.motor[2].ChangeDutyCycle(init - DC)
                await asyncio.sleep(self.PWMSLEEP)


class servoMotor:
    '''
    Contorl servo motors with the Raspberry Pi GPIO. Not
    yet functional.
    '''

    def __init__(self, PWM, PWMFREQ=50, PWMSLEEP=100e-6):
        GPIO.setmode(GPIO.BOARD) # define pin numbering scheme
        GPIO.setup(PWM, GPIO.OUT) # setup servo pin

        self.PWM = GPIO.PWM(PWM, PWMFREQ)
        self.PWM.start(0)

        self.PWMFREQ = PWMFREQ
        self.PWMSLEEP = PWMSLEEP

    def setPos(self, val): # val should be between 0 & 180
        # convert angle in degrees to duty cycle in pencentage for a 1-2ms pulse
        dutyCycle = self.PWMFREQ*(val+180)/1800
        self.PWM.ChangeDutyCycle(dutyCycle)


class robotMotor:
    '''
    Application specific motor control for Raspberry Pi
    robot. Controls two DC motors (or two sets of two
    motors if wired in parallel) and one servo motor.
    '''

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
        '''
        Drives robot forward. The driveTime parameter
        specifies the number of seconds running before
        stopping and speed parameter takes a value from
        0 to 100 to determine motor PWM.
        '''

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
        '''
        Drives robot in reverse. The driveTime parameter
        specifies the number of seconds running before
        stopping and speed parameter takes a value from
        0 to 100 to determine motor PWM.
        '''

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
        '''
        Drives robot left gently. The driveTime parameter
        specifies the number of seconds running before
        stopping and speed parameter takes a value from
        0 to 100 to determine motor PWM.
        '''

        self.left.fwd()
        self.right.fwd()
        await self.right.inc(final=speed)
        await asyncio.sleep(driveTime)
        await self.right.dec(init=speed)
        self.left.stop()
        self.right.stop()

    async def softRight(self, driveTime=0.5, speed=100):
        '''
        Drives robot right gently. The driveTime parameter
        specifies the number of seconds running before
        stopping and speed parameter takes a value from
        0 to 100 to determine motor PWM.
        '''

        self.left.fwd()
        self.right.fwd()
        await self.left.inc(final=speed)
        await asyncio.sleep(driveTime)
        await self.left.dec(init=speed)
        self.left.stop()
        self.right.stop()

    async def hardLeft(self, driveTime=0.5, speed=100):
        '''
        Drives robot left aggresively. The driveTime
        parameter specifies the number of seconds running
        before stopping and speed parameter takes a value
        from 0 to 100 to determine motor PWM.
        '''

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
        '''
        Drives robot right aggresively. The driveTime
        parameter specifies the number of seconds running
        before stopping and speed parameter takes a value
        from 0 to 100 to determine motor PWM.
        '''

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
        ''' Lowers servo to 'down' position.
        '''

        self.servo.setPos(0)

    def servoUp(self):
        ''' Raises servo to 'up' position.
        '''

        self.servo.setPos(90)


class server:
    '''
    Server methods for streaming video and streaming commands
    for the Raspberry Pi robot.
    '''

    async def cmdRoutine(self, reader, writer, commands):
        '''
        Coroutine function to handle cmdServer connections.
        The reader and writer parameters are required. The
        asyncio.start_server() function passes reader and
        writer objects which are used to read and write data
        to the stream. The commands parameter takes the
        robot's main command list and writes to it directly
        as a mutable object.
        '''

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
        '''
        Establishes command server using asyncio's stream
        APIs. Accepts connections from any IP on port 8888.
        Uses cmdRoutine to handle connections.
        '''

        server = await asyncio.start_server(
            lambda reader, writer: self.cmdRoutine(
                reader, writer, commands), '0.0.0.0', 8888)

        addr = server.sockets[0].getsockname()
        print(f'Serving commands on {addr}')

        async with server:
            await server.serve_forever()

    async def vidRoutine(self, reader, writer):
        '''
        Coroutine function to handle vidServer connections.
        The reader and writer parameters are required. The
        asyncio.start_server() function passes reader and
        writer objects which are used to read and write data
        to the stream.

        Video from the Rasberry Pi's camera is transmitted
        at 640x480p and encoded as h264.
        '''

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
        '''
        Establishes video server using asyncio's stream
        APIs. Accepts connections from any IP on port 7777.
        Uses cmdRoutine to handle connections.
        '''

        server = await asyncio.start_server(
            self.vidRoutine, '0.0.0.0', 7777)

        addr = server.sockets[0].getsockname()
        print(f'Serving video on {addr}')

        async with server:
            await server.serve_forever()



async def control(cmds):
    '''
    Main control method for Raspberry Pi robot. Function
    accepts commands via local keybaord input or remote
    client as written to cmds list parameter. Local
    commands take precedence. Function executes commands
    via its robotMotor object. Most recent command is
    always executed and previously accumulated commands
    are erased.
    '''

    motor = robotMotor()
    kb = KBHit()
    local = True
    localDict = {True:'local', False:'remote'}

    # main contorl loop
    while True:
        await asyncio.sleep(0)
        cmd = ''

        # check for local commands
        if kb.kbhit():
            cmd = kb.getch()
            local = True

        # check for remote commands
        elif cmds:
            cmd = cmds[-1]
            cmds.clear()
            local = False

        # check for exit command
        if cmd == 'e':
            break

        # check for contorl commands
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

    # main commands list written to by cmdServer and read
    # from by control funciton
    cmds = []

    cmdsvr = server()
    vidsvr = server()

    # run control loop, cmdServer & vidServer concurrently
    await asyncio.gather(control(cmds),
        cmdsvr.cmdServer(cmds),vidsvr.vidServer())


try:
    asyncio.run(main())
finally:
    GPIO.cleanup()