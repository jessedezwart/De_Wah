import RPi.GPIO as GPIO
import time

# set gpio mode
GPIO.setmode(GPIO.BCM)

# set pins
left_engine_pins = [17,4,3,2]
right_engine_pins = [27,22,10,9]

for pin in left_engine_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)
for pin in right_engine_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)


# halfstep sequence via datasheet
# https://www.raspberrypi-spy.co.uk/wp-content/uploads/2012/07/Stepper-Motor-28BJY-48-Datasheet.pdf
halfstep_seq = [
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1],
    [1,0,0,1]
]

# halfstep sequence for reversal
halfstep_seq_rev = [
    [1,0,0,1],
    [0,0,0,1],
    [0,0,1,1],
    [0,0,1,0],
    [0,1,1,0],
    [0,1,0,0],
    [1,1,0,0],
    [1,0,0,0]
]


def left_forward():
    for halfstep in range(8):
        for pin in range(4):
            GPIO.output(left_engine_pins[pin], halfstep_seq[halfstep][pin])
        time.sleep(0.001)


def right_forward():
    for halfstep in range(8):
        for pin in range(4):
            GPIO.output(right_engine_pins[pin], halfstep_seq[halfstep][pin])
        time.sleep(0.001)



def left_reverse():
    for halfstep in range(8):
        for pin in range(4):
            GPIO.output(left_engine_pins[pin], halfstep_seq_rev[halfstep][pin])
        time.sleep(0.001)


def right_reverse():
    for halfstep in range(8):
        for pin in range(4):
            GPIO.output(right_engine_pins[pin], halfstep_seq_rev[halfstep][pin])
        time.sleep(0.001)