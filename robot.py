

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
        self.motor = (IN1,IN2,self.PWM) # create motor object

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

    # def inc(self, initDC=0, finalDC=100):
    #     if initDC < finalDC:
    #         for DC in range(finalDC-initDC):
    #             self.PWM.ChangeDutyCycle(initDC + DC)
    #             time.sleep(self.PWMSLEEP)

    # def dec(self, initDC=100, finalDC=0):
    #     if initDC > finalDC:
    #         for DC in range(initDC-finalDC):
    #             self.PWM.ChangeDutyCycle(initDC - DC)
    #             time.sleep(self.PWMSLEEP)




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
servoMotor = servoMotor(SERVOPWM)

leftMotor.fwd()
rightMotor.fwd()

leftMotor.inc()
time.sleep(1)
rightMotor.inc()
time.sleep(1)
leftMotor.dec()
rightMotor.dec()

del leftMotor
del rightMotor

servoMotor.setPos(0)
time.sleep(1)
servoMotor.setPos(90)
time.sleep(1)
servoMotor.setPos(180)

del servoMotor