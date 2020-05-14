import RPi.GPIO as GPIO
import time

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

    def inc(self, init=0, final=100):
        if init < final:
            for DC in range(final-init):
                self.motor[2].ChangeDutyCycle(init + DC)
                time.sleep(self.PWMSLEEP)

    def dec(self, init=100, final=0):
        if init > final:
            for DC in range(init-final):
                self.motor[2].ChangeDutyCycle(init - DC)
                time.sleep(self.PWMSLEEP)


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

    def fwd(self, driveTime=0.5, speed=100):
        self.left.fwd()
        self.right.fwd()
        self.left.inc(final=speed)
        self.right.inc(final=speed)
        time.sleep(driveTime)
        self.left.dec(init=speed)
        self.right.dec(init=speed)
        self.left.stop()
        self.right.stop()

    def rev(self, driveTime=0.5, speed=100):
        self.left.rev()
        self.right.rev()
        self.left.inc(final=speed)
        self.right.inc(final=speed)
        time.sleep(driveTime)
        self.left.dec(init=speed)
        self.right.dec(init=speed)
        self.left.stop()
        self.right.stop()

    def softLeft(self, driveTime=0.5, speed=100):
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
        time.sleep(driveTime)
        self.left.dec(init=speed)
        self.left.stop()
        self.right.stop()

    def hardLeft(self, driveTime=0.5, speed=100):
        self.left.rev()
        self.right.fwd()
        self.left.inc(final=speed/2)
        self.right.inc(final=speed)
        time.sleep(driveTime)
        self.left.dec(init=speed/2)
        self.right.dec(init=speed)
        self.left.stop()
        self.right.stop()

    def hardRight(self, driveTime=0.5, speed=100):
        self.left.fwd()
        self.right.rev()
        self.left.inc(final=speed)
        self.right.inc(final=speed/2)
        time.sleep(driveTime)
        self.left.dec(init=speed)
        self.right.dec(init=speed/2)
        self.left.stop()
        self.right.stop()


class camera:

    def __init__(self):
        pass


class server:

    def __init__(self):
        pass



motorControl = robotMotor()
exitKey = False
while exitKey is False:

    keyCmd = input()
    keyCmd.lower()
    if keyCmd is 'e':
        exitKey = True
    elif keyCmd is '5':
        motorControl.fwd()
    elif keyCmd is '2':
        motorControl.rev()
    elif keyCmd is '1':
        motorControl.softLeft()
    elif keyCmd is '4':
        motorControl.hardLeft()
    elif keyCmd is '3':
        motorControl.softRight()
    elif keyCmd is '6':
        motorControl.hardRight()

GPIO.cleanup()