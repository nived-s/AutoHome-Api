from gpiozero import Servo
from time import sleep

servo = Servo(25)

def rotate_0_to_90():
    val = -1
    try:
        while val <= 0:
            servo.value = val
            sleep(0.1)
            val += 0.1
    except KeyboardInterrupt:
        print("Rotation stopped")

def rotate_90_to_0():
    val = 0
    try:
        while val >= -1:
            servo.value = val
            sleep(0.1)
            val -= 0.1
    except KeyboardInterrupt:
        print("Rotation stopped")

try:
    while True:
        rotate_0_to_90()
        rotate_90_to_0()
except KeyboardInterrupt:
    print("Program stopped")
