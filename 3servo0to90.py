import RPi.GPIO as GPIO
import time

# Use the Broadcom SOC channel
GPIO.setmode(GPIO.BCM)

# Set up the GPIO channels
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

# Create PWM objects with a 50Hz frequency
pwm1 = GPIO.PWM(17, 50)
pwm2 = GPIO.PWM(27, 50)
pwm3 = GPIO.PWM(22, 50)

# Start PWM with a 0% duty cycle
pwm1.start(0)
pwm2.start(0)
pwm3.start(0)

# Rotate the servo motors from 0 to 90 degrees
for angle in range(0, 91, 5):
    duty_cycle = angle / 18 + 2
    pwm1.ChangeDutyCycle(duty_cycle)
    pwm2.ChangeDutyCycle(duty_cycle)
    pwm3.ChangeDutyCycle(duty_cycle)
    time.sleep(0.05)

# Stop PWM and clean up the GPIO channels
pwm1.stop()
pwm2.stop()
pwm3.stop()
GPIO.cleanup()
