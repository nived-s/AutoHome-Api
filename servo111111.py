#WORKING TESTED ON MARCH 20
# Signal pin No-7 (GPIO 4 )
# Power pin No-2 (5V power)
# GND pin No-6 (GROUND)
import RPi.GPIO as GPIO
import time

# Set up GPIO
servo_pin = 7  # Use any GPIO pin
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(servo_pin, GPIO.OUT)

# Create PWM object
pwm = GPIO.PWM(servo_pin, 50)  # 50 Hz frequency

# Rotate the servo motor
try:
    pwm.start(7.5)  # Initial position
    time.sleep(2)

    pwm.ChangeDutyCycle(12.5)  # Rotate to 90 degrees
    time.sleep(1)

    pwm.ChangeDutyCycle(2.5)  # Rotate to 180 degrees
    time.sleep(2)

except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()