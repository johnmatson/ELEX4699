AIN1 = 11
AIN2 = 13
APWM = 15
BIN1 = 29
BIN2 = 31
BPWM = 33
SERVOPWM = 32

PWMFREQ = 10e3



# import RPi.GPIO library
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

import time

# define pin numbering scheme
GPIO.setmode(GPIO.BOARD)

# setup left motor pins
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(APWM, GPIO.OUT)

# setup right motor pins
GPIO.setup(BIN1, GPIO.OUT)
GPIO.setup(BIN2, GPIO.OUT)
GPIO.setup(BPWM, GPIO.OUT)

# setup servo motor pins
GPIO.setup(SERVOPWM, GPIO.OUT)

# create PWM pin variables
leftPWM = GPIO.PWM(APWM, PWMFREQ)
rightPWM = GPIO.PWM(BPWM, PWMFREQ)
servoPWM = GPIO.PWM(SERVOPWM, PWMFREQ)

# create motor "objects"
leftMotor = [AIN1,AIN2,leftPWM]
rightMotor = [BIN1,BIN2,rightPWM]

def motorFwd(motor):
    GPIO.output(motor[0], GPIO.LOW)
    GPIO.output(motor[1], GPIO.HIGH)

def motorRev(motor):
    GPIO.output(motor[0], GPIO.HIGH)
    GPIO.output(motor[1], GPIO.LOW)

def motorInit(motor):
    motor[3].start(0)

def motorIncrease(motor, initDC=0, finalDC=100):
    if initDC < finalDC:
        for DC in range(finalDC-initDC):
            motor[3].ChangeDutyCycle(initDC + DC)
            time.sleep(100e-3)

def motorDecrease(motor, initDC=100, finalDC=0):
    if initDC > finalDC:
        for DC in range(initDC-finalDC):
            motor[3].ChangeDutyCycle(initDC - DC)
            time.sleep(100e-3)
    



motorInit(leftMotor)
motorInit(rightMotor)
motorFwd(leftMotor)
motorFwd(rightMotor)
motorIncrease(leftMotor)
time.sleep(1)
motorIncrease(rightMotor)
time.sleep(3)
motorDecrease(leftMotor)
motorDecrease(rightMotor)



GPIO.cleanup()