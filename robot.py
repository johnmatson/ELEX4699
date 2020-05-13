

# exitKey = False
# while exitKey is False:

#     # read keyboard input
#     keyCmd = input()
#     keyCmd.lower()
#     if keyCmd is 'e':
#         exitKey = True

#     # 





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
        self.motor = (IN1,IN2,PWM) # create motor object

        self.PWMSLEEP = PWMSLEEP


    def fwd(self):
        GPIO.output(self.motor[0], GPIO.LOW)
        GPIO.output(self.motor[1], GPIO.HIGH)

    def rev(self):
        GPIO.output(self.motor[0], GPIO.HIGH)
        GPIO.output(self.motor[1], GPIO.LOW)

    def inc(self, initDC=0, finalDC=100):
        if initDC < finalDC:
            for DC in range(finalDC-initDC):
                self.motor[2].ChangeDutyCycle(initDC + DC)
                time.sleep(self.PWMSLEEP)

    def dec(self, initDC=100, finalDC=0):
        if initDC > finalDC:
            for DC in range(initDC-finalDC):
                self.motor[2].ChangeDutyCycle(initDC - DC)
                time.sleep(self.PWMSLEEP)
    
    def __del__(self):
        GPIO.cleanup()


class piMotor:

    # pins constants
    AIN1 = 11
    AIN2 = 13
    APWM = 15
    BIN1 = 29
    BIN2 = 31
    BPWM = 33
    SERVOPWM = 32

    #  misc constants
    PWMFREQ = 10e3
    PWMSLEEP = 100e-6

    # create PWM pin variables
    leftPWM = GPIO.PWM(APWM, PWMFREQ)
    rightPWM = GPIO.PWM(BPWM, PWMFREQ)
    servoPWM = GPIO.PWM(SERVOPWM, PWMFREQ)

    # create motor "objects"
    leftMotor = (AIN1,AIN2,leftPWM)
    rightMotor = (BIN1,BIN2,rightPWM)

    motorDict = {'left':leftMotor, 'right':rightMotor}

    def __init__(self):
        # define pin numbering scheme
        GPIO.setmode(GPIO.BOARD)

        # setup left motor pins
        GPIO.setup(self.AIN1, GPIO.OUT)
        GPIO.setup(self.AIN2, GPIO.OUT)
        GPIO.setup(self.APWM, GPIO.OUT)

        # setup right motor pins
        GPIO.setup(self.BIN1, GPIO.OUT)
        GPIO.setup(self.BIN2, GPIO.OUT)
        GPIO.setup(self.BPWM, GPIO.OUT)

        # setup servo motor pins
        GPIO.setup(self.SERVOPWM, GPIO.OUT)

    def fwd(self, motorDes):
        motor = self.motorDict[motorDes]
        GPIO.output(motor[0], GPIO.LOW)
        GPIO.output(motor[1], GPIO.HIGH)

    def rev(self, motorDes):
        motor = self.motorDict[motorDes]
        GPIO.output(motor[0], GPIO.HIGH)
        GPIO.output(motor[1], GPIO.LOW)

    def init(self, motorDes):
        motor = self.motorDict[motorDes]
        motor[2].start(0)

    def increase(self, motorDes, initDC=0, finalDC=100):
        motor = self.motorDict[motorDes]
        if initDC < finalDC:
            for DC in range(finalDC-initDC):
                motor[2].ChangeDutyCycle(initDC + DC)
                time.sleep(self.PWMSLEEP)

    def decrease(self, motorDes, initDC=100, finalDC=0):
        motor = self.motorDict[motorDes]
        if initDC > finalDC:
            for DC in range(initDC-finalDC):
                motor[2].ChangeDutyCycle(initDC - DC)
                time.sleep(self.PWMSLEEP)
    
    def __del__(self):
        GPIO.cleanup()



# motor = piMotor()
# motor.init('left')
# motor.init('right')
# motor.fwd('left')
# motor.fwd('right')
# motor.increase('left')
# time.sleep(1)
# motor.increase('right')
# time.sleep(3)
# motor.decrease('left')
# motor.decrease('right')



# pins constants
AIN1 = 11
AIN2 = 13
APWM = 15
BIN1 = 29
BIN2 = 31
BPWM = 33
SERVOPWM = 32

leftMotor = dcMotor(AIN1, AIN2, APWM)
rightMotor = dcMotor(BIN1, BIN2, BPWM)

leftMotor.fwd()
rightMotor.fwd()

leftMotor.inc()
time.sleep(1)
rightMotor.inc()
time.sleep(1)
leftMotor.dec()
rightMotor.dec()
