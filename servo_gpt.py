import RPi.GPIO as GPIO
import time

# Set up GPIO
servo_pin = 7  # Use any GPIO pin
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(servo_pin, GPIO.OUT)

# Create PWM object
pwm = GPIO.PWM(servo_pin, 50)  # 50 Hz frequency

# Initial position of the servo motor
initial_position = 7.5

def on_DOOR():
    # Rotate the servo motor to 90 degrees
    pwm.ChangeDutyCycle(12.5)
    time.sleep(1)

    print("Door opened")

def off_DOOR():
    # Rotate the servo motor to 0 degrees
    pwm.ChangeDutyCycle(2.5)
    time.sleep(1)

    # Rotate the servo motor back to the initial position
    pwm.ChangeDutyCycle(initial_position)
    time.sleep(1)

    print("Door closed")

# Start the servo motor at the initial position
pwm.start(initial_position)

try:
    while True:
        # Open the door
        on_DOOR()

        # Wait for some time
        time.sleep(5)

        # Close the door
        off_DOOR()

        # Wait for some time
        time.sleep(5)

except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()