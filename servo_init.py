from gpiozero import Servo
from time import sleep

servo = Servo(17)
 
 
try:
    while True:
        servo.min()
        sleep(0.5)
        servo.mid()
        sleep(0.5)
        
except KeyboardInterrupt:
    print("oh noo")