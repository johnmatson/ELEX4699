AIN1 = 11
AIN2 = 13
APWM = 15
BIN1 = 29
BIN2 = 31
BPWM = 33
SERVOPWM = 32

PWMFREQ = 10e3

leftMotor = (AIN1,AIN1,APWM)
rightMotor = (BIN1,BIN1,BPWM)

# import RPi.GPIO library
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

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
leftWheel = GPIO.PWM(APWM, PWMFREQ)
rightWheel = GPIO.PWM(BPWM, PWMFREQ)
servo = GPIO.PWM(SERVOPWM, PWMFREQ)

# start PWM with 0% duty cycle
leftWheel.start(0)
rightWheel.start(0)
servo.start(0)

def motorFwd(motor):
    GPIO.output(motor[0], GPIO.LOW)
    GPIO.output(motor[1], GPIO.HIGH)

def motorRev(motor):
    GPIO.output(motor[0], GPIO.HIGH)
    GPIO.output(motor[1], GPIO.LOW)



motorFwd(leftMotor)
motorFwd(rightMotor)

for i in range(5):
    for dutyCycle in range(1000):
        leftWheel.ChangeDutyCycle(dutyCycle/10)
    for dutyCycle in range(1000):
        leftWheel.ChangeDutyCycle(100 - dutyCycle/10)

    for dutyCycle in range(1000):
        rightWheel.ChangeDutyCycle(dutyCycle/10)
    for dutyCycle in range(1000):
        rightWheel.ChangeDutyCycle(100 - dutyCycle/10)



GPIO.cleanup()