import requests
from flask import Flask, jsonify
import requests
import time
from mq2_sensor import MQ2Sensor  # Assuming you have a library for interfacing with the MQ2 sensor
from flask import Flask, jsonify, request
from smokedetfeatures.powermanage import init_power_management
import RPi.GPIO as GPIO
from datetime import datetime, timedelta
import json
import threading  # Add import statement for threading module
import schedule



app = Flask(__name__)

#-------------------------------AWAY FUNCTION-----------------------------------------
def away():
    

    # Define GPIO pins for servo motor control
    DOOR_SERVO_PIN = 18  # Example pin for controlling door with servo motor, adjust as needed
    WINDOW_SERVO_PIN = 23  # Example pin for controlling window with servo motor, adjust as needed
    GATE_SERVO_PIN = 24  # Example pin for controlling gate with servo motor, adjust as needed
    IR_SENSOR_PIN = 23  # Example pin for IR sensor, adjust as needed
    LDR_PIN = 24  # Example pin for LDR sensor, adjust as needed
    LIGHT_PIN = 11 #pin for checking status of light
    DHT11_PIN = 25 #pin for checking temp/humid status

    # Flask API endpoint
    API_ENDPOINT = "http://localhost:5000"

    # Initialize GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(DOOR_SERVO_PIN, GPIO.OUT)
    GPIO.setup(WINDOW_SERVO_PIN, GPIO.OUT)
    GPIO.setup(GATE_SERVO_PIN, GPIO.OUT)
    GPIO.setup(IR_SENSOR_PIN, GPIO.IN)
    GPIO.setup(LDR_PIN, GPIO.IN)



    # Read data from DHT11 sensor
    def read_dht11_data():
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT11_PIN)
        if humidity is not None and temperature is not None:
            result = {'temperature': temperature, 'humidity': humidity}
        else:
            result = {'temperature': None, 'humidity': None}

        return result

    # Function to control servo motor to close door
    def close_door():
        # Check if the door is open
        door_status = GPIO.input(DOOR_SERVO_PIN)
        if door_status == GPIO.LOW:  # If door is open, close it
            GPIO.output(DOOR_SERVO_PIN, GPIO.HIGH)
            print("Door closed")
        else:
            print("Door is already closed")

    # Function to control servo motor to close window
    def close_window():
        # Check if the window is open
        window_status = GPIO.input(WINDOW_SERVO_PIN)
        if window_status == GPIO.LOW:  # If window is open, close it
            GPIO.output(WINDOW_SERVO_PIN, GPIO.HIGH)
            print("Window closed")
        else:
            print("Window is already closed")

    # Function to control servo motor to close gate
    def close_gate():
        # Check if the gate is open
        gate_status = GPIO.input(GATE_SERVO_PIN)
        if gate_status == GPIO.LOW:  # If gate is open, close it
            GPIO.output(GATE_SERVO_PIN, GPIO.HIGH)
            print("Gate closed")
        else:
            print("Gate is already closed")

    # Function to close all elements using servo motors
    def close_elements():
        close_door()
        close_window()
        close_gate()

        # Post data to Flask API after closing elements
        data = {
            "door_status": "closed",
            "window_status": "closed",
            "gate_status": "closed"
        }
        requests.post(API_ENDPOINT + "/close_elements", json=data)


    # Function to turn off all power appliances
    def turn_off_power_appliances():
        # Code to turn off all power appliances
        print("Turning off all power appliances")

    # Function to check for intrusion or movement using IR sensor
    def check_intrusion():
        if GPIO.input(IR_SENSOR_PIN):
            print("Intrusion or movement detected")
            # Post message to Flask API
            message = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                       "event": "Intrusion or movement detected"}
            requests.post(API_ENDPOINT + "/intrusion_detection", json=message)

    # Function to monitor light levels using LDR sensor
    def monitor_light_levels():
        while True:
            light_value = GPIO.input(LDR_PIN)
            # Check if light level is unusual (adjust threshold as needed)
            if light_value < 100:  # Example threshold for unusual light level
                print("Unusual light level detected")
                # Post message to Flask API
                message = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                           "event": "Unusual light level detected",
                           "light_value": light_value}
                requests.post(API_ENDPOINT + "/unusual_light_detection", json=message)
            time.sleep(60)  # Check light level every minute
 
    #
    def light_status():
        light_status = json.loads(request.data)
        light_status_bool = light_status['light_status']
        print(light_status_bool)
        #setting GPIO pin 11 to output
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18,GPIO.OUT)

        if light_status_bool == "1":
            # light is on
            print('light is on')
            GPIO.output(11,GPIO.HIGH)
        else:
            # ligh is off
            print('light is off')
            GPIO.output(11,GPIO.LOW)


        return jsonify({ 'msg': 'success.' }), 201 

    # Main function
    def main():
        try:

            # Reading temp/humidity
            read_dht11_data()
        
            # Check light status
            light_status()
        
            # Close elements using servo motor
            close_elements()

            # Turn off power appliances
            turn_off_power_appliances()

            # Start monitoring for intrusion using IR sensor
            GPIO.add_event_detect(IR_SENSOR_PIN, GPIO.RISING, callback=check_intrusion)

            # Start monitoring light levels using LDR sensor
            monitor_light_levels()

        except KeyboardInterrupt:
            GPIO.cleanup()


#--------------------------END OF AWAY FUNCTION-----------------------------------

#-------------------------------AMBIENT FUNCTION-----------------------------------------
def ambient():
    #-----------------------------------------need to add flask api----------------------------------------------------------------------------------------
    # Define GPIO pin for LDR sensor
    LDR_PIN = 18  # Example pin for LDR sensor, adjust as needed

    # Initialize GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LDR_PIN, GPIO.IN)

    # Function to read light intensity from LDR sensor
    def read_ldr():
        return GPIO.input(LDR_PIN)

    # Function to calculate color temperature based on light intensity and current time
    def calculate_color_temperature(ldr_value):
        # Daytime vs. nighttime detection based on current time
        current_time = datetime.now().time()
        daytime = datetime.strptime("06:00:00", "%H:%M:%S").time() <= current_time <= datetime.strptime("18:00:00", "%H:%M:%S").time()

        # Adjust color temperature based on light intensity and daytime/nighttime
        if daytime:
            if ldr_value > 800:  # High light intensity (bright sunlight)
                return "Cool" # Use cooler color temperature (e.g., bluish-white light)
            elif ldr_value > 400:  # Moderate light intensity (cloudy or shaded)
                return "Neutral" # Use neutral color temperature
            else:  # Low light intensity (dawn, dusk, or overcast conditions)
                return "Warm" # Use warm color temperature (e.g., yellowish-white light)
        else:  # Nighttime
            if ldr_value > 200:  # Moderate light intensity (streetlights or indoor lighting)
                return "Neutral" # Use neutral color temperature
            else:  # Low light intensity (darkness)
                return "Warm" # Use warm color temperature (e.g., yellowish-white light)

    # Function to control lights based on color temperature
    def control_lights(color_temperature):
        # Code to control lights based on color temperature goes here
        # This could involve adjusting LED brightness or color, or controlling smart bulbs
        print(f"Setting color temperature to: {color_temperature}")

    # Main function
    def main():
        try:
            while True:
                # Read light intensity from LDR sensor
                ldr_value = read_ldr()

                # Control lights based on color temperature
                control_lights(calculate_color_temperature(ldr_value))

                # Sleep for 10 seconds
                time.sleep(10)

        except KeyboardInterrupt:
            # Clean up GPIO on keyboard interrupt
            GPIO.cleanup()


#--------------------------END OF AMBIENT FUNCTION-----------------------------------

#-------------------------------CHILDELDER FUNCTION-----------------------------------------
def childelder():
    # GPIO pins connected to the signal pins of the IR sensors at the door and gate
    DOOR_SENSOR_PIN = 17
    GATE_SENSOR_PIN = 18

    # GPIO pin connected to the HVAC system
    HVAC_PIN = 23

    # GPIO pin connected to the LIGHT system
    LIGHT_PIN = 11

    # Initialize GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(DOOR_SENSOR_PIN, GPIO.IN)
    GPIO.setup(GATE_SENSOR_PIN, GPIO.IN)
    GPIO.setup(HVAC_PIN, GPIO.OUT)
    GPIO.setup(LIGHT_PIN, GPIO.OUT)

    # Function for light status to turn on/off
    def light_status():
        light_status = json.loads(request.data)
        light_status_bool = light_status['light_status']
        print(light_status_bool)

        if light_status_bool == "1":
            # light is on
            print('light is on')
            GPIO.output(LIGHT_PIN, GPIO.HIGH)  # Correct GPIO pin number
        else:
            # light is off
            print('light is off')
            GPIO.output(LIGHT_PIN, GPIO.LOW)  # Correct GPIO pin number

        return jsonify({ 'msg': 'success.' }), 201 

    # Function to monitor movement and send alerts
    def monitor_movement():
        while True:
            door_motion = GPIO.input(DOOR_SENSOR_PIN)
            gate_motion = GPIO.input(GATE_SENSOR_PIN)
        
            if door_motion or gate_motion:
                entry_point = "Door" if door_motion else "Gate"
                message = f"Child/Elder Motion detected at {entry_point} at {time.ctime()}"
                send_notification(message)
                # Turn on HVAC when movement is detected
                control_hvac(True)
            else:
                # Turn off HVAC when no movement is detected
                control_hvac(False)
        
            time.sleep(0.1)

    # Function to send notification
    def send_notification(message):
        data = {'notification': message}
        response = requests.post('http://localhost:5000/alerts', json=data)
        if response.status_code != 200:
            print('Failed to send notification:', response.text)

    # Function to control HVAC system
    def control_hvac(state):
        GPIO.output(HVAC_PIN, state)

    # Initialize Flask app
    app = Flask(__name__)

    # Route to receive alerts
    @app.route('/alerts', methods=['POST'])
    def receive_alert():
        data = request.json
        print('Received alert:', data)
        return jsonify({'status': 'success'})

    # Route to control light
    @app.route('/light_status', methods=['POST'])
    def light_status_info():
        light_status()
        return jsonify({'status': 'success'})

    # Route to control HVAC
    @app.route('/control_hvac', methods=['POST'])
    def control_hvac_route():
        data = request.json
        hvac_state = data.get('state')
        if hvac_state is not None:
            control_hvac(hvac_state)
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

    if __name__ == '__main__':
        try:
            # Start monitoring movement in a separate thread
            movement_thread = threading.Thread(target=monitor_movement)
            movement_thread.start()
        
            # Run the Flask app
            app.run(host='0.0.0.0', port=5000)
        except KeyboardInterrupt:
            GPIO.cleanup()
#--------------------------END OF CHILDELEDER FUNCTION-----------------------------------

#-------------------------------GUEST FUNCTION-----------------------------------------
def guest():

    # GPIO pins connected to the signal pins of the IR sensors at the door and gate
    DOOR_SENSOR_PIN = 17
    GATE_SENSOR_PIN = 18

    # Initialize GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(DOOR_SENSOR_PIN, GPIO.IN)
    GPIO.setup(GATE_SENSOR_PIN, GPIO.IN)

    # Dictionary to track the last known state of each entry point (door/gate)
    last_state = {
        DOOR_SENSOR_PIN: GPIO.input(DOOR_SENSOR_PIN),
        GATE_SENSOR_PIN: GPIO.input(GATE_SENSOR_PIN)
    }

    # Function to monitor movement and determine direction
    def monitor_movement():
        while True:
            door_motion = GPIO.input(DOOR_SENSOR_PIN)
            gate_motion = GPIO.input(GATE_SENSOR_PIN)
        
            if door_motion != last_state[DOOR_SENSOR_PIN]:
                entry_point = "Door"
                direction = "arrived" if door_motion else "left"
                message = f"Guest {direction} through {entry_point} at {time.ctime()}"
                send_notification(message)
                last_state[DOOR_SENSOR_PIN] = door_motion
        
            if gate_motion != last_state[GATE_SENSOR_PIN]:
                entry_point = "Gate"
                direction = "arrived" if gate_motion else "left"
                message = f"Guest {direction} through {entry_point} at {time.ctime()}"
                send_notification(message)
                last_state[GATE_SENSOR_PIN] = gate_motion
        
            time.sleep(0.1)

    # Function to send notification
    def send_notification(message):
        data = {'notification': message}
        response = requests.post('http://localhost:5000/alerts', json=data)
        if response.status_code != 200:
            print('Failed to send notification:', response.text)

    #add feature to override energy consumption mode
    # Flag to indicate whether energy consumption mode is active
    energy_saver_mode = False


    # Function to override energy consumption mode
    def override_energy_consumption():
        global energy_consumption_mode
        energy_saver_mode = False
        print("Energy consumption mode overridden.")
        
    def main():
        try:
            monitor_movement()
        except KeyboardInterrupt:
            GPIO.cleanup()        



#--------------------------END OF GUEST FUNCTION-----------------------------------

#-------------------------------NIGHT FUNCTION-----------------------------------------
def night():
    # Define GPIO pin for LDR sensor
    LDR_PIN = 18  # Example pin for LDR sensor, adjust as needed

    # Define the GPIO pin for LED sensor
    LED_PIN = 25

    # Define GPIO pin for DHT11 sensor
    DHT11_PIN = 11

    # Define GPIO pin for PIR sensor
    PIR_PIN = 11

    # Initialize GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LDR_PIN, GPIO.IN)
    GPIO.setup(DHT11_PIN, GPIO.IN)
    GPIO.setup(LED_PIN, GPIO.IN)
    GPIO.setup(PIR_PIN, GPIO.IN)

    # Function to read light intensity from LDR sensor
    def read_ldr():
        return GPIO.input(LDR_PIN)


    def read_dht():
        return GPIO.input(DHT11_pin)
    # Function to adjust lights for sleep based on user-defined sleep timings
    def adjust_lights_for_sleep(ldr_value):
        # Get user-defined sleep timings from Flask API
        response = requests.get('http://localhost:5000/sleep-timings')

        if response.status_code == 200:
            sleep_timings = response.json()
            sleep_start = datetime.strptime(sleep_timings['sleep_start'], '%H:%M:%S').time()
            sleep_end = datetime.strptime(sleep_timings['sleep_end'], '%H:%M:%S').time()

            # Check if it's nighttime and if the current time is within sleep timings
            current_time = datetime.now().time()
            nighttime = not (datetime.strptime("06:00:00", "%H:%M:%S").time() <= current_time <= datetime.strptime("18:00:00", "%H:%M:%S").time())
            if nighttime and sleep_start <= current_time <= sleep_end:

                ldr_value = read_ldr()
                 # Adjust LED based on LDR value
                if ldr_value > 800:  # High light intensity
                    GPIO.output(LED_PIN, GPIO.LOW)  # Dim the LED
                elif ldr_value > 400:  # Moderate light intensity
                    GPIO.output(LED_PIN, GPIO.LOW)  # Dim the LED
                else:  # Low light intensity
                    GPIO.output(LED_PIN, GPIO.HIGH)  # Turn off the LED
                # Code to reduce or dim the lights or turn off the lights goes here
                print("Adjusting lights for sleep...")
            else:
                print("Not adjusting lights for sleep.")
        else:
            print('Failed to retrieve sleep timings:', response.text)



    # Function to adjust temperature
    def adjust_temp_for_sleep(dht_value):
        # Get user-defined sleep timings from Flask API
        response = requests.get('http://localhost:5000/sleep-timings')

        if response.status_code == 200:
            sleep_timings = response.json()
            sleep_start = datetime.strptime(sleep_timings['sleep_start'], '%H:%M:%S').time()
            sleep_end = datetime.strptime(sleep_timings['sleep_end'], '%H:%M:%S').time()

            # Check if it's nighttime and if the current time is within sleep timings
            current_time = datetime.now().time()
            nighttime = not (datetime.strptime("06:00:00", "%H:%M:%S").time() <= current_time <= datetime.strptime("18:00:00", "%H:%M:%S").time())
            if nighttime and sleep_start <= current_time <= sleep_end:
                # Code to reduce or dim the lights or turn off the lights goes here
                print("Adjusting temperature and humidity for sleep...")
            else:
                print("Not adjusting temperature and humidity for sleep.")
        else:
            print('Failed to retrieve sleep timings:', response.text)

    # Code for movement in sleep
    def detect_sleep():
        # Initialize variables
        motion_count = 0
        sleep_threshold = 3  # Number of consecutive readings with no motion to detect sleep

        while True:
            if read_pir() == GPIO.LOW:
                motion_count = 0  # Reset motion count if motion is detected
            else:
                motion_count += 1  # Increment motion count if no motion is detected

            # If motion count exceeds the sleep threshold, consider occupants to have gone to sleep
            if motion_count >= sleep_threshold:
                return True
            else:
                return False

    # Function to control servo motor to close door
    def close_door():
        # Check if the door is open
        door_status = GPIO.input(DOOR_SERVO_PIN)
        if door_status == GPIO.LOW:  # If door is open, close it
            GPIO.output(DOOR_SERVO_PIN, GPIO.HIGH)
            print("Door closed")
        else:
            print("Door is already closed")

    # Function to control servo motor to close window
    def close_window():
        # Check if the window is open
        window_status = GPIO.input(WINDOW_SERVO_PIN)
        if window_status == GPIO.LOW:  # If window is open, close it
            GPIO.output(WINDOW_SERVO_PIN, GPIO.HIGH)
            print("Window closed")
        else:
            print("Window is already closed")

    # Function to control servo motor to close gate
    def close_gate():
        # Check if the gate is open
        gate_status = GPIO.input(GATE_SERVO_PIN)
        if gate_status == GPIO.LOW:  # If gate is open, close it
            GPIO.output(GATE_SERVO_PIN, GPIO.HIGH)
            print("Gate closed")
        else:
            print("Gate is already closed")

    # Function to close all elements using servo motors
    def close_elements():
        close_door()
        close_window()
        close_gate()

        # Post data to Flask API after closing elements
        data = {
            "door_status": "closed",
            "window_status": "closed",
            "gate_status": "closed"
        }
        requests.post(API_ENDPOINT + "/close_elements", json=data)

    # Main function
    def main():
        try:
            while True:
                # Closing, windows, gates and doors
                close_elements()

                # Detecting whether occupants have went to sleep or not
                if detect_sleep():
                    print("Occupants have gone to sleep.")
                else:
                    print("Occupants are awake.")

                # Read light intensity from LDR sensor
                ldr_value = read_ldr()

                # Control lights based on night time
                adjust_lights_for_sleep(ldr_value)

                time.sleep(10)  # Read LDR sensor every 10 seconds

        except KeyboardInterrupt:
            GPIO.cleanup()  # Clean up GPIO on keyboard interrupt


#--------------------------END OF NIGHT FUNCTION-----------------------------------

#-------------------------------VACAY FUNCTION-----------------------------------------
def vacay():

    # Define GPIO pins for servo motor control
    DOOR_SERVO_PIN = 18  # Example pin for controlling door with servo motor, adjust as needed
    WINDOW_SERVO_PIN = 23  # Example pin for controlling window with servo motor, adjust as needed
    GATE_SERVO_PIN = 24  # Example pin for controlling gate with servo motor, adjust as needed
    IR_SENSOR_PIN = 23  # Example pin for IR sensor, adjust as needed
    LDR_PIN = 24  # Example pin for LDR sensor, adjust as needed
    LIGHT_PIN = 11 # pin for controlling light
    FAN_pin = 23 #pin for fan controlling
    AC_pin = 24 #pin for ac controlling
    DHT11_PIN = 25 # Set up DHT11 sensor


    # Flask API endpoint
    API_ENDPOINT = "http://localhost:5000"

    # Initialize GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(DOOR_SERVO_PIN, GPIO.OUT)
    GPIO.setup(WINDOW_SERVO_PIN, GPIO.OUT)
    GPIO.setup(GATE_SERVO_PIN, GPIO.OUT)
    GPIO.setup(IR_SENSOR_PIN, GPIO.IN)
    GPIO.setup(LDR_PIN, GPIO.IN)
    GPIO.setup(FAN_pin, GPIO.OUT)
    GPIO.setup(AC_pin, GPIO.OUT)

    # Read data from DHT11 sensor and change the values# Adding predefined temp & humidity, HVAC system turned on to minimuize heating/cooling suitable conditions maintained to prevent mold or freezing pipes

    def read_dht11_data():
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT11_PIN)
        if humidity is not None and temperature is not None:
            # Check temperature thresholds
            if temperature <= 0:
                # Temperature too low, turn on fan
                fan_status('on')
            elif temperature >= 55:
                # Temperature too high, turn on AC
                ac_status('on')
        
            # Check humidity threshold
            if humidity >= 80:
                # Humidity too high, turn on AC
                ac_status('on')

            result = {'temperature': temperature, 'humidity': humidity}
        else:
            result = {'temperature': None, 'humidity': None}

        return result

    #--------scheduling ac and fan-------------
    def schedule_ac_and_fan():
        # Define intervals and durations for turning on the AC and fan
        AC_INTERVAL = 9  # Interval in hours
        FAN_INTERVAL = 9  # Interval in hours
        DURATION = 5  # Duration in minutes

        # Define functions to turn on/off the AC and fan
        def turn_on(device):
            device('on')

        def turn_off(device):
            device('off')

        # Function to schedule AC and fan operations
        def schedule_ac_and_fan():
            devices = {'AC': ac_status, 'Fan': fan_status}

            for device, status in devices.items():
                schedule.every(AC_INTERVAL if device == 'AC' else FAN_INTERVAL).hours.do(turn_on, status)
                schedule.every(AC_INTERVAL if device == 'AC' else FAN_INTERVAL).hours.do(turn_off, status).after(DURATION).minutes

            # Main loop to execute scheduled tasks
            while True:
                schedule.run_pending()
                time.sleep(1)

    # Function to control servo motor to close door
    def close_door():
        # Check if the door is open
        door_status = GPIO.input(DOOR_SERVO_PIN)
        if door_status == GPIO.LOW:  # If door is open, close it
            GPIO.output(DOOR_SERVO_PIN, GPIO.HIGH)
            print("Door closed")
        else:
            print("Door is already closed")

    # Function to control servo motor to close window
    def close_window():
        # Check if the window is open
        window_status = GPIO.input(WINDOW_SERVO_PIN)
        if window_status == GPIO.LOW:  # If window is open, close it
            GPIO.output(WINDOW_SERVO_PIN, GPIO.HIGH)
            print("Window closed")
        else:
            print("Window is already closed")

    # Function to control servo motor to close gate
    def close_gate():
        # Check if the gate is open
        gate_status = GPIO.input(GATE_SERVO_PIN)
        if gate_status == GPIO.LOW:  # If gate is open, close it
            GPIO.output(GATE_SERVO_PIN, GPIO.HIGH)
            print("Gate closed")
        else:
            print("Gate is already closed")

    # Function to close all elements using servo motors
    def close_elements():
        close_door()
        close_window()
        close_gate()

        # Post data to Flask API after closing elements
        data = {
            "door_status": "closed",
            "window_status": "closed",
            "gate_status": "closed"
        }
        requests.post(API_ENDPOINT + "/close_elements", json=data)


    # Function to turn off all power appliances
    def turn_off_power_appliances():
        # Code to turn off all power appliances
        print("Turning off all power appliances")

    # Function to check for intrusion or movement using IR sensor
    def check_intrusion():
        if GPIO.input(IR_SENSOR_PIN):
            print("Intrusion or movement detected")
            # Post message to Flask API
            message = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                       "event": "Intrusion or movement detected"}
            requests.post(API_ENDPOINT + "/intrusion_detection", json=message)

    # Function to monitor light levels using LDR sensor
    def monitor_light_levels():
        while True:
            light_value = GPIO.input(LDR_PIN)
            # Check if light level is unusual (adjust threshold as needed)
            if light_value < 100:  # Example threshold for unusual light level
                print("Unusual light level detected")
                # Post message to Flask API
                message = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                           "event": "Unusual light level detected",
                           "light_value": light_value}
                requests.post(API_ENDPOINT + "/unusual_light_detection", json=message)
            time.sleep(60)  # Check light level every minute
 
    # To deter potential theft and robbery

    # Initialize GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.OUT)

    # Define function to handle light status
    def light_status():
        data = json.loads(request.data)
        light_status_bool = data.get('light_status')
        print(f"Light is {'on' if light_status_bool == '1' else 'off'}")
        GPIO.output(11, GPIO.HIGH if light_status_bool == '1' else GPIO.LOW)
        # Schedule turning off the light after 30 minutes
        if light_status_bool == '1':
            schedule.every(9).hours.do(lambda: GPIO.output(11, GPIO.LOW)).tag('light_off')
        return jsonify({'msg': 'success.'}), 201

    @app.route('/api/light_status', methods=['POST'])
    def handle_light_status():
        return light_status()

    # Start the scheduler loop
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)


    # Main function
    def main():
        try:
        
            # Call the scheduling function
            schedule_ac_and_fan()
            # Reading temp and humid 
            read_dht_data()

            # Check light status
            light_status()
        
            # Close elements using servo motor
            close_elements()

            # Turn off power appliances
            turn_off_power_appliances()

            # Start monitoring for intrusion using IR sensor
            GPIO.add_event_detect(IR_SENSOR_PIN, GPIO.RISING, callback=check_intrusion)

            # Start monitoring light levels using LDR sensor
            monitor_light_levels()

        except KeyboardInterrupt:
            GPIO.cleanup()


#--------------------------END OF VACAY FUNCTION-----------------------------------

#-------------------------------EMERGENCY FUNCTION-----------------------------------------
def emergency():
    # Function to detect smoke and determine severity level
    def detect_smoke():
        mq2_sensor = MQ2Sensor()  # Initialize the MQ2 sensor
        smoke_ppm = mq2_sensor.read_ppm()  # Read smoke concentration in ppm

        # Define severity levels based on ppm ranges
        if smoke_ppm < 200:
            severity = "Low"
        elif 200 <= smoke_ppm < 700:
            severity = "Moderately High"
        elif 700 <= smoke_ppm < 4000:
            severity = "High"
        else:
            severity = "Dangerous"

        return smoke_ppm, severity

    # Function to retrieve user address from Flask API
    def get_user_address():
        # Send GET request to Flask API to retrieve user's address
        response = requests.get("http://localhost:5000/user/address")

        # Extract user's address from the response JSON
        user_address = response.json().get("address")
        return user_address

    # Function to fetch emergency numbers from Emergency Number API
    def get_emergency_numbers():
        url = "https://emergencynumberapi.com/api/?country_code=US"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "police": data.get("police"),
                "fire": data.get("fire"),
                "ambulance": data.get("ambulance")
            }
        else:
            return None

    # Function to send emergency alert
    def send_emergency_alert(address, severity, local_services):
        # Extract local emergency numbers
        police_number = local_services.get("police")
        fire_number = local_services.get("fire")
        ambulance_number = local_services.get("ambulance")

        # Compose message with address and severity
        message = f"Emergency at {address}. Severity: {severity}"

        # Send alert to local emergency services
        requests.post(police_number, json={"message": message})
        requests.post(fire_number, json={"message": message})
        requests.post(ambulance_number, json={"message": message})
    
    # Function to activate power management
    def activate_power_management():
        # Turn off all electrical appliances
        # Here, you can add code to control other GPIO pins to turn off appliances
        # For demonstration purposes, let's print a message
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"The power appliances are turned off as the smoke detected is moderately high at {time_now}"
        print("Activating power management:", message)

        # Switch electricity of home to backup generators or battery backups
        GPIO.output(POWER_RELAY_PIN, GPIO.LOW)

        # Post message to Flask API
        requests.post("http://localhost:5000/power_off", json={"message": message})

    # Function to switch to backup generators or battery
    def switch_to_backup():
        # Here, you can add code to switch to backup generators or battery
        # For demonstration purposes, let's print a message
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"The backup generators or battery have been switched on at {time_now}"
        print("Switching to backup generators or battery:", message)

        # Post message to Flask API
        requests.post("http://localhost:5000/switch_to_backup", json={"message": message})

    # Route to retrieve stored smoke detection events
    @app.route('/smoke_events', methods=['GET'])
    def get_smoke_events():
        return jsonify(smoke_events), 200

    # Route to handle power off event
    @app.route('/power_off', methods=['POST'])
    def power_off():
        request_data = request.json
        message = request_data.get("message")
        print("Received power off message:", message)
        # Perform any additional actions if required
        return jsonify({"status": "Received power off message"}), 200

    # Route to handle switch to backup event
    @app.route('/switch_to_backup', methods=['POST'])
    def switch_to_backup():
        request_data = request.json
        message = request_data.get("message")
        print("Received switch to backup message:", message)
        # Perform any additional actions if required
        return jsonify({"status": "Received switch to backup message"}), 200


    # Route to send emergency alert
    @app.route('/emergency_alert', methods=['POST'])
    def emergency_alert():
        # Example request body: {"address": "123 Main St", "severity": "high"}
        request_data = request.json
        address = request_data.get("address")
        severity = request_data.get("severity")

        # Fetch local emergency numbers
        local_services = get_emergency_numbers()

        if local_services:
            # Send emergency alert
            send_emergency_alert(address, severity, local_services)
            return jsonify({"status": "Emergency alert sent"}), 200
        else:
            return jsonify({"error": "Failed to fetch emergency numbers"}), 500

    # Route to send notification to the user
    @app.route('/send_notification', methods=['POST'])
    def send_notification():
        # Example request body: {"message": "Notification message"}
        request_data = request.json
        message = request_data.get("message")

        # Send notification to the user
        user_endpoint = "http://localhost:5000/user/notification"
        response = requests.post(user_endpoint, json={"message": message})

        if response.status_code == 200:
            return jsonify({"status": "Notification sent"}), 200
        else:
            return jsonify({"error": "Failed to send notification"}), 500

    # Main function
    def main():
        while True:
            # Detect smoke and determine severity
            smoke_ppm, severity = detect_smoke()
        
            #running power management
            init_power_management()

            # If smoke is detected
            if severity != "Moderate":
                # Retrieve user's address from Flask API
                user_address = get_user_address()

                # Send emergency alert
                response = requests.post("http://localhost:5000/emergency_alert", json={"address": user_address, "severity": severity})
                if response.status_code == 200:
                    print("Emergency alert sent successfully.")
                else:
                    print("Failed to send emergency alert.")

                # Send notification to the user
                response = requests.post("http://localhost:5000/send_notification", json={"message": "Emergency alert: " + severity})
                if response.status_code == 200:
                    print("Notification sent successfully.")
                else:
                    print("Failed to send notification.")

            time.sleep(300)  # Check for smoke every 5 minutes


#--------------------------END OF EMERGENCY FUNCTION-----------------------------------

#-------------------------------ENERGY SAVER FUNCTION-----------------------------------------
#--------------------------END OF ENERGY SAVER FUNCTION-----------------------------------




# Define a dictionary to store modes
modes = {
    'Away': 'Turns off all the appliances,locks all windows, doors and gates',
    'Ambient': 'Turns on ambient lights, a mood setter',
    'Guest': 'Monitor and track guest movements to provide them hospitality',
    'Child and Elder': 'Monitor and track movements to provide them supervision',
    'Emergency': 'Enable emergency and evacuation protocols',
    'Night': 'Prepare for a restful night and sound sleep',
    'Energy Saver': 'Save application from overusage and reduce electricity bill',
    'Vacay': 'Turns off all the appliances, locks all windows, doors and gates, ensuring safety for a long leave from home',
}

# Define a route to handle GET requests
@app.route('/api/data', methods=['GET'])
def get_modes():
    selected_mode = request.args.get('mode')
    if selected_mode:
        main(selected_mode)
    return jsonify(modes)

def main(selected_mode):
    # Implement the logic for each mode here
    if selected_mode == 'Away':
        away()
        print('Away mode enabled')
    if selected_mode == 'Ambient':
        print('Ambient mode enabled')
    if selected_mode == 'Guest':
        print('Guest mode enabled')
    if selected_mode == 'Child and Elder':
        print('Child and Elder mode enabled')
    if selected_mode == 'Emergency':
        print('Emergency mode enabled')
    if selected_mode == 'Night':
        print('Night mode enabled')
    if selected_mode == 'Energy Saver':
        print('Energy Saver mode enabled')
    if selected_mode == 'Vacay':
        print('Vacay mode enabled')

if __name__ == '__main__':
    app = Flask(__name__)
    # Define a route to handle GET requests
    @app.route('/api/data', methods=['GET'])
    def get_modes():
        selected_mode = request.args.get('mode')
        if selected_mode:
            main(selected_mode)
        return jsonify(modes)

    # Start the scheduler loop in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()

    app.run(debug=True, host='0.0.0.0', port=8000)
         
         