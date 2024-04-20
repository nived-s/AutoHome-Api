import requests
from flask import Flask, jsonify
import os
import sys
import RPi.GPIO as GPIO
import requests
import json
from datetime import datetime
import Adafruit_DHT
from flask import Flask, request, make_response, jsonify
import io
 #from mq2_sensor import MQ2Sensor
import time
import board
import busio  
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


app = Flask(__name__)
#-------------------------------LIVING ROOM FUNCTION-----------------------------------------
def living_room():
    # Setup GPIO pins
    light_pin = 18
    fan_pin = 23
    ac_pin = 24

    # Set up DHT11 sensor
    DHT11_PIN = 25

    # Set up Window and door
    window_pin = 11
    door_pin = 16

    # Initialize GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(light_pin, GPIO.OUT)
    GPIO.setup(fan_pin, GPIO.OUT)
    GPIO.setup(ac_pin, GPIO.OUT)
    GPIO.setup(door_pin, GPIO.OUT)
    GPIO.setup(window_pin, GPIO.OUT)
    dht_device = adafruit_dht.DHT11(board.D4)
    
    # Read data from DHT11 sensor
    def read_dht11_data():
        while True:
            try:
                temperature_c = dht_device.temperature
                temperature_f = temperature_c*(9 / 5) + 32
                humidity = dht_device.humidity
                print("Temp:{:.1f} C / {:.1f} F    Humidity: {}%".format(temperature_c, temperature_f, humidity))
            except RuntimeError as err:
                print(err.args[0])

            time.sleep(1)

    # Light status management
    def light_status(status):
        if status == 'on':
            GPIO.output(light_pin, GPIO.HIGH)
        elif status == 'off':
            GPIO.output(light_pin, GPIO.LOW)

    # Fan status management
    def fan_status(status):
        if status == 'on':
            GPIO.output(fan_pin, GPIO.HIGH)
        elif status == 'off':
            GPIO.output(fan_pin, GPIO.LOW)

    # AC status management
    def ac_status(status):
        if status == 'on':
            GPIO.output(ac_pin, GPIO.HIGH)
        elif status == 'off':
            GPIO.output(ac_pin, GPIO.LOW)

    # Function to get status of the door
    def door_status():
        if status == 'open':
            GPIO.input(door_pin, GPIO.HIGH)
        elif status == 'closed':
            GPIO.input(door_pin, GPIO.LOW)
        

    # Function to get status of the window
    def window_status():
        if status == 'open':
            GPIO.input(window_pin, GPIO.HIGH)
        elif status == 'closed':
            GPIO.input(window_pin, GPIO.LOW)
 
    def read_image(living_room):
        #filename = 'uploads\\123.jpg'
        #---------------or---------------
        """image_path = f'uploads/{pid}.jpg'  # Adjust the path based on your file structure
        try:
            with open(image_path, 'rb') as image_file:
                return image_file.read()
        except FileNotFoundError:
            return None
        """
        #---------------or------- ---------
        image_url = f'https://res.cloudinary.com/dmfwpz555/image/upload/rooms/living_room.jpg'  # Replace with the actual URL

        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            return response.content
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as err:
            print(f"Error: {err}")
            return None
        # Implement this function to read the image file based on the provided PID
        # Example: Read image from file system or database
        # Return image data as bytes or None if PID is invalid
    

    @app.route('/images/living_room.jpg', methods=['GET'])
    def get_image(living_room):
        image_binary = read_image(living_room)
        response = make_response(image_binary)
        response.headers.set('Content-Type', 'image/jpeg')
        response.headers.set(
            'Content-Disposition', 'attachment', filename='%s.jpg' % living_room)
        return response, send_file(
        io.BytesIO(image_binary),
        mimetype='image/jpeg',
        as_attachment=True,
        download_name='%s.jpg' % living_room)
           
     # Create the /status endpoint
    @app.route('/api/status', methods=['GET'])
    def status():
        light = GPIO.input(light_pin)
        fan = GPIO.input(fan_pin)
        ac = GPIO.input(ac_pin)
        dh11_data = read_dht11_data()
        door = door_status()
        window = window_status()

        status = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'light': 'on' if light == GPIO.HIGH else 'off',
            'fan': 'on' if fan == GPIO.HIGH else 'off',
            'ac': 'on' if ac == GPIO.HIGH else 'off',
            'temperature': dh11_data['temperature'],
            'humidity': dh11_data['humidity'],
            'door_status': 'open' if door == GPIO.HIGH else 'closed',
            'window': 'open' if window == GPIO.HIGH else 'closed',
        }

        return jsonify(status)

    # Define a route to handle GET requests for counting active devices
    @app.route('/api/device_count', methods=['GET'])
    def device_count():
        devices = {
            'light': GPIO.input(light_pin),
            'fan': GPIO.input(fan_pin),
            'ac': GPIO.input(ac_pin),
            'door': GPIO.input(door_pin),
            'window': GPIO.input(window_pin),
        }

        active_devices = sum(devices.values())

        return jsonify({'active_devices': active_devices})

    # Define a route to handle POST requests for controlling the devices
    @app.route('/api/control', methods=['POST'])
    def control_devices():
        req_data = request.get_json()

        if 'devices' in req_data:
            devices = req_data['devices']

            for device_name, status in devices.items():
                if device_name == 'light':
                    light_status(status)
                elif device_name == 'fan':
                    fan_status(status)
                elif device_name == 'ac':
                    ac_status(status)
                elif device_name == 'door':
                    door_status(status)
                    # Update the door status after setting its value
                    status_dict = {'door_status': 'open' if GPIO.input(door_pin) else 'closed'}
                elif device_name == 'window':
                    window_status(status)
                    # Update the window status after setting its value
                    status_dict = {'window': 'open' if GPIO.input(window_pin) else 'closed'}

                if device_name in ['light', 'fan', 'ac']:
                    # Update the status of the controllable device
                    status_dict[device_name] = 'on' if status == 'true' else 'off'

            # Return the updated status in the response
            return jsonify(status_dict)

        else:
            return jsonify({'error': 'No devices specified in the request'}), 400




#--------------------------END OF LIVING ROOM FUNCTION-----------------------------------

#-------------------------------KITCHEN FUNCTION-----------------------------------------
def kitchen():

    ## need to add smoke detector function called,which is emergency mode,if smoke is detected, later on, 

    # Initialize the MQ2 sensor
    mq7_channel = AnalogIn(ads, ADS.P1)


    # Setup GPIO pins
    light_pin = 18
    fan_pin = 23
    ac_pin = 24
    door_pin = 11
    window_pin = 16
    smoke_pin = 9

    # Set up DHT11 sensor
    DHT11_PIN = 25

    # Initialize GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(light_pin, GPIO.OUT)
    GPIO.setup(fan_pin, GPIO.OUT)
    GPIO.setup(ac_pin, GPIO.OUT)
    GPIO.setup(door_pin, GPIO.OUT)
    GPIO.setup(window_pin, GPIO.OUT)
    GPIO.setup(smoke_pin, GPIO.OUT)
    dht_device = adafruit_dht.DHT11(board.D4)

    # Define the conversion factor for the ADC (mV per bit)
    conversion_factor = 3.0 / 32768.0

    # Define the lookup table for the MQ-7 sensor
    mq7_lut = [
        0, 50, 100, 200, 500, 1000, 2000, 5000, 10000
    ]

    # Read data from DHT11 sensor
    def read_dht11_data():
        while True:
            try:
                temperature_c = dht_device.temperature
                temperature_f = temperature_c*(9 / 5) + 32
                humidity = dht_device.humidity
                print("Temp:{:.1f} C / {:.1f} F    Humidity: {}%".format(temperature_c, temperature_f, humidity))
            except RuntimeError as err:
                print(err.args[0])

            time.sleep(1)


    def read_channel(channel):
        value = channel.value
        voltage = value * conversion_factor * 6.144
        return voltage

    def read_mq7(value):
        closest_index = min(range(len(mq7_lut)), key=lambda i: abs(mq7_lut[i]-value))
        """print("MQ-7 value: {:.2f} ppm".format(
            mq7_ppm
        ))
        time.sleep(1)"""
        closest_ppm = mq7_lut[clost_index][0]
        # Return the smoke detection value
        return closest_ppm
    
    # Smoke detection management
    def smoke_status(status):
        if status == 'smoke detected':
            mq7_ppm = read_mq7(value)
            print("MQ-7 value: {:.2f} ppm".format(
                mq7_ppm
            ))
        elif status == 'no smoke detected':
            pass

    # Light status management
    def light_status(status):
        if status == 'on':
            GPIO.output(light_pin, GPIO.HIGH)
        elif status == 'off':
            GPIO.output(light_pin, GPIO.LOW)

    # Fan status management
    def fan_status(status):
        if status == 'on':
            GPIO.output(fan_pin, GPIO.HIGH)
        elif status == 'off':
            GPIO.output(fan_pin, GPIO.LOW)

    # AC status management
    def ac_status(status):
        if status == 'on':
            GPIO.output(ac_pin, GPIO.HIGH)
        elif status == 'off':
            GPIO.output(ac_pin, GPIO.LOW)

    # Function to get status of the door
    def door_status():
        if GPIO.input(door_pin) == GPIO.HIGH:
            return 'open'
        else:
            return 'closed'

    # Function to get status of the window
    def window_status():
        if GPIO.input(window_pin) == GPIO.HIGH:
            return 'open'
        else:
            return 'closed'
 
    def read_image(kitchen):
        #filename = 'uploads\\123.jpg'
        #---------------or---------------
        """image_path = f'uploads/{pid}.jpg'  # Adjust the path based on your file structure
        try:
            with open(image_path, 'rb') as image_file:
                return image_file.read()
        except FileNotFoundError:
            return None
        """
        #---------------or----------------
        image_url = f'https://res.cloudinary.com/dmfwpz555/image/upload/rooms/kitchen.jpg'  # Replace with the actual URL

        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            return response.content
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as err:
            print(f"Error: {err}")
            return None
        # Implement this function to read the image file based on the provided PID
        # Example: Read image from file system or database
        # Return image data as bytes or None if PID is invalid
    

    @app.route('/images/kitchen.jpg', methods=['GET'])
    def get_image(kitchen):
        image_binary = read_image(kitchen)
        response = make_response(image_binary)
        response.headers.set('Content-Type', 'image/jpeg')
        response.headers.set(
            'Content-Disposition', 'attachment', filename='%s.jpg' % kitchen)
        return response, send_file(
        io.BytesIO(image_binary),
        mimetype='image/jpeg',
        as_attachment=True,
        download_name='%s.jpg' % kitchen)
    
    # Create the /status endpoint
    @app.route('/api/status', methods=['GET'])
    def status():
        smoke = mq2_sensor.get_smoke_status()
        light = GPIO.input(light_pin)
        fan = GPIO.input(fan_pin)
        ac = GPIO.input(ac_pin)
        dh11_data = read_dht11_data()
        door = door_status()
        window = window_status()

        status = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'light': 'on' if light == GPIO.HIGH else 'off',
            'fan': 'on' if fan == GPIO.HIGH else 'off',
            'ac': 'on' if ac == GPIO.HIGH else 'off',
            'smoke':'smoke detected' if smoke else 'no smoke detected',
            'temperature': dh11_data['temperature'],'humidity': dh11_data['humidity'],
            'door_status': 'open' if door == 'open' else 'closed',
            'window': 'open' if window == 'open' else 'closed',
        }

        return jsonify(status)

    # Define a route to handle GET requests for counting active devices
    @app.route('/api/device_count', methods=['GET'])
    def device_count():
        devices = {
            'light': GPIO.input(light_pin),
            'fan': GPIO.input(fan_pin),
            'ac': GPIO.input(ac_pin),
            'door': GPIO.input(door_pin),
            'window': GPIO.input(window_pin),
        }

        active_devices = sum(devices.values())

        return jsonify({'active_devices': active_devices})

    # Define a route tohandle POST requests for controlling the devices
    @app.route('/api/control', methods=['POST'])
    def control_devices():
        req_data = request.get_json()

        if 'devices' in req_data:
            devices = req_data['devices']

            for device_name, status in devices.items():
                if device_name == 'light':
                    light_status(status)
                elif device_name == 'fan':
                    fan_status(status)
                elif device_name == 'ac':
                    ac_status(status)
                elif device_name == 'door':
                    if status == 'open':
                        GPIO.output(door_pin, GPIO.LOW)
                    elif status == 'close':
                        GPIO.output(door_pin, GPIO.HIGH)
                elif device_name == 'window':
                    if status == 'open':
                        GPIO.output(window_pin, GPIO.LOW)
                    elif status == 'close':
                        GPIO.output(door_pin, GPIO.HIGH)
                elif device_name == 'smoke':
                    if status == 'smoke detected':
                        mq7_ppm = read_mq7(value)
                        print("MQ-7 value: {:.2f} ppm".format(mq7_ppm))
                    elif status == 'no smoke detected':
                        #mq2_sensor.clear_smoke()
                        pass

        return jsonify({'status': 'Devices updated'})

#--------------------------END OF KITCHEN FUNCTION-----------------------------------

#-------------------------------GUEST BEDROOM FUNCTION-----------------------------------------
def guest_bedroom():

    # Setup GPIO pins
    light_pin = 18
    fan_pin = 23
    ac_pin = 24

    # Set up DHT11 sensor
    DHT11_PIN = 25

    # Set up Window and door
    window_pin = 11
    door_pin = 16

    # Initialize GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(light_pin, GPIO.OUT)
    GPIO.setup(fan_pin, GPIO.OUT)
    GPIO.setup(ac_pin, GPIO.OUT)
    GPIO.setup(door_pin, GPIO.OUT)
    GPIO.setup(window_pin, GPIO.OUT)
    dht_device = adafruit_dht.DHT11(board.D4)


    # Read data from DHT11 sensor
    def read_dht11_data():
        while True:
            try:
                temperature_c = dht_device.temperature
                temperature_f = temperature_c*(9 / 5) + 32
                humidity = dht_device.humidity
                print("Temp:{:.1f} C / {:.1f} F    Humidity: {}%".format(temperature_c, temperature_f, humidity))
            except RuntimeError as err:
                print(err.args[0])

            time.sleep(1)
    # Light status management
    def light_status(status):
        if status == 'on':
            GPIO.output(light_pin, GPIO.HIGH)
        elif status == 'off':
            GPIO.output(light_pin, GPIO.LOW)

    # Fan status management
    def fan_status(status):
        if status == 'on':
            GPIO.output(fan_pin, GPIO.HIGH)
        elif status == 'off':
            GPIO.output(fan_pin, GPIO.LOW)

    # AC status management
    def ac_status(status):
        if status == 'on':
            GPIO.output(ac_pin, GPIO.HIGH)
        elif status == 'off':
            GPIO.output(ac_pin, GPIO.LOW)

    # Function to get status of the door
    def door_status():
        if status == 'open':
            GPIO.input(door_pin, GPIO.HIGH)
        elif status == 'closed':
            GPIO.input(door_pin, GPIO.LOW)
        

    # Function to get status of the window
    def window_status():
        if status == 'open':
            GPIO.input(window_pin, GPIO.HIGH)
        elif status == 'closed':
            GPIO.input(window_pin, GPIO.LOW)
 
 
    def read_image(guest_room):
        #filename = 'uploads\\123.jpg'
        #---------------or---------------
        """image_path = f'uploads/{pid}.jpg'  # Adjust the path based on your file structure
        try:
            with open(image_path, 'rb') as image_file:
                return image_file.read()
        except FileNotFoundError:
            return None
        """
        #---------------or----------------
        image_url = f'https://res.cloudinary.com/dmfwpz555/image/upload/rooms/guest_room.jpg'  # Replace with the actual URL

        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            return response.content
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as err:
            print(f"Error: {err}")
            return None
        # Implement this function to read the image file based on the provided PID
        # Example: Read image from file system or database
        # Return image data as bytes or None if PID is invalid
    

    @app.route('/images/guest_room.jpg', methods=['GET'])
    def get_image(guest_room):
        image_binary = read_image(guest_room)
        response = make_response(image_binary)
        response.headers.set('Content-Type', 'image/jpeg')
        response.headers.set(
            'Content-Disposition', 'attachment', filename='%s.jpg' % guest_room)
        return response, send_file(
        io.BytesIO(image_binary),
        mimetype='image/jpeg',
        as_attachment=True,
        download_name='%s.jpg' % guest_room)
    
     # Create the /status endpoint
    @app.route('/api/status', methods=['GET'])
    def status():
        light = GPIO.input(light_pin)
        fan = GPIO.input(fan_pin)
        ac = GPIO.input(ac_pin)
        dh11_data = read_dht11_data()
        door = door_status()
        window = window_status()

        status = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'light': 'on' if light == GPIO.HIGH else 'off',
            'fan': 'on' if fan == GPIO.HIGH else 'off',
            'ac': 'on' if ac == GPIO.HIGH else 'off',
            'temperature': dh11_data['temperature'],
            'humidity': dh11_data['humidity'],
            'door_status': 'open' if door == GPIO.HIGH else 'closed',
            'window': 'open' if window == GPIO.HIGH else 'closed',
        }

        return jsonify(status)

    # Define a route to handle GET requests for counting active devices
    @app.route('/api/device_count', methods=['GET'])
    def device_count():
        devices = {
            'light': GPIO.input(light_pin),
            'fan': GPIO.input(fan_pin),
            'ac': GPIO.input(ac_pin),
            'door': GPIO.input(door_pin),
            'window': GPIO.input(window_pin),
        }

        active_devices = sum(devices.values())

        return jsonify({'active_devices': active_devices})
    # Define a route to handle POST requests for controlling the devices
    @app.route('/api/control', methods=['POST'])
    def control_devices():
        req_data = request.get_json()

        if 'devices' in req_data:
            devices = req_data['devices']

            for device_name, status in devices.items():
                if device_name == 'light':
                    light_status(status)
                elif device_name == 'fan':
                    fan_status(status)
                elif device_name == 'ac':
                    ac_status(status)
                elif device_name == 'door':
                    door_status(status)
                    # Update the door status after setting its value
                    status_dict = {'door_status': 'open' if GPIO.input(door_pin) else 'closed'}
                elif device_name == 'window':
                    window_status(status)
                    # Update the window status after setting its value
                    status_dict = {'window': 'open' if GPIO.input(window_pin) else 'closed'}

                if device_name in ['light', 'fan', 'ac']:
                    # Update the status of the controllable device
                    status_dict[device_name] = 'on' if status == 'true' else 'off'

            # Return the updated status in the response
            return jsonify(status_dict)

        else:
            return jsonify({'error': 'No devices specified in the request'}), 400


    
#--------------------------END OF GUEST BEDROOM FUNCTION-----------------------------------

#-------------------------------CHILDREN BEDROOM FUNCTION-----------------------------------------
def children_bedroom():

    # Setup GPIO pins
    light_pin = 18
    fan_pin = 23
    ac_pin = 24

    # Set up DHT11 sensor
    DHT11_PIN = 25

    # Set up Window and door
    window_pin = 11
    door_pin = 16

    # Initialize GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(light_pin, GPIO.OUT)
    GPIO.setup(fan_pin, GPIO.OUT)
    GPIO.setup(ac_pin, GPIO.OUT)
    GPIO.setup(door_pin, GPIO.OUT)
    GPIO.setup(window_pin, GPIO.OUT)
    dht_device = adafruit_dht.DHT11(board.D4)


    # Read data from DHT11 sensor
    def read_dht11_data():
        while True:
            try:
                temperature_c = dht_device.temperature
                temperature_f = temperature_c*(9 / 5) + 32
                humidity = dht_device.humidity
                print("Temp:{:.1f} C / {:.1f} F    Humidity: {}%".format(temperature_c, temperature_f, humidity))
            except RuntimeError as err:
                print(err.args[0])

            time.sleep(1)

    # Light status management
    def light_status(status):
        if status == 'on':
            GPIO.output(light_pin, GPIO.HIGH)
        elif status == 'off':
            GPIO.output(light_pin, GPIO.LOW)

    # Fan status management
    def fan_status(status):
        if status == 'on':
            GPIO.output(fan_pin, GPIO.HIGH)
        elif status == 'off':
            GPIO.output(fan_pin, GPIO.LOW)

    # AC status management
    def ac_status(status):
        if status == 'on':
            GPIO.output(ac_pin, GPIO.HIGH)
        elif status == 'off':
            GPIO.output(ac_pin, GPIO.LOW)

    # Function to get status of the door
    def door_status():
        if status == 'open':
            GPIO.input(door_pin, GPIO.HIGH)
        elif status == 'closed':
            GPIO.input(door_pin, GPIO.LOW)
        

    # Function to get status of the window
    def window_status():
        if status == 'open':
            GPIO.input(window_pin, GPIO.HIGH)
        elif status == 'closed':
            GPIO.input(window_pin, GPIO.LOW)
 
    def read_image(children_bedroom):
        #filename = 'uploads\\123.jpg'
        #---------------or---------------
        """image_path = f'uploads/{pid}.jpg'  # Adjust the path based on your file structure
        try:
            with open(image_path, 'rb') as image_file:
                return image_file.read()
        except FileNotFoundError:
            return None
        """
        #---------------or----------------
        image_url = f'https://res.cloudinary.com/dmfwpz555/image/upload/rooms/children_bedroom.jpg'  # Replace with the actual URL

        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            return response.content
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as err:
            print(f"Error: {err}")
            return None
        # Implement this function to read the image file based on the provided PID
        # Example: Read image from file system or database
        # Return image data as bytes or None if PID is invalid
    

    @app.route('/images/<int:pid>.jpg', methods=['GET'])
    def get_image(children_bedroom):
        image_binary = read_image(children_bedroom)
        response = make_response(image_binary)
        response.headers.set('Content-Type', 'image/jpeg')
        response.headers.set(
            'Content-Disposition', 'attachment', filename='%s.jpg' % children_bedroom)
        return response, send_file(
        io.BytesIO(image_binary),
        mimetype='image/jpeg',
        as_attachment=True,
        download_name='%s.jpg' % children_bedroom)
          
     # Create the /status endpoint
    @app.route('/api/status', methods=['GET'])
    def status():
        light = GPIO.input(light_pin)
        fan = GPIO.input(fan_pin)
        ac = GPIO.input(ac_pin)
        dh11_data = read_dht11_data()
        door = door_status()
        window = window_status()

        status = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'light': 'on' if light == GPIO.HIGH else 'off',
            'fan': 'on' if fan == GPIO.HIGH else 'off',
            'ac': 'on' if ac == GPIO.HIGH else 'off',
            'temperature': dh11_data['temperature'],
            'humidity': dh11_data['humidity'],
            'door_status': 'open' if door == GPIO.HIGH else 'closed',
            'window': 'open' if window == GPIO.HIGH else 'closed',
        }

        return jsonify(status)

    # Define a route to handle GET requests for counting active devices
    @app.route('/api/device_count', methods=['GET'])
    def device_count():
        devices = {
            'light': GPIO.input(light_pin),
            'fan': GPIO.input(fan_pin),
            'ac': GPIO.input(ac_pin),
            'door': GPIO.input(door_pin),
            'window': GPIO.input(window_pin),
        }

        active_devices = sum(devices.values())

        return jsonify({'active_devices': active_devices})

    # Define a route to handle POST requests for controlling the devices
    @app.route('/api/control', methods=['POST'])
    def control_devices():
        req_data = request.get_json()

        if 'devices' in req_data:
            devices = req_data['devices']

            for device_name, status in devices.items():
                if device_name == 'light':
                    light_status(status)
                elif device_name == 'fan':
                    fan_status(status)
                elif device_name == 'ac':
                    ac_status(status)
                elif device_name == 'door':
                    door_status(status)
                    # Update the door status after setting its value
                    status_dict = {'door_status': 'open' if GPIO.input(door_pin) else 'closed'}
                elif device_name == 'window':
                    window_status(status)
                    # Update the window status after setting its value
                    status_dict = {'window': 'open' if GPIO.input(window_pin) else 'closed'}

                if device_name in ['light', 'fan', 'ac']:
                    # Update the status of the controllable device
                    status_dict[device_name] = 'on' if status == 'true' else 'off'

            # Return the updated status in the response
            return jsonify(status_dict)

        else:
            return jsonify({'error': 'No devices specified in the request'}), 400


#--------------------------END OF CHILDREN BEDROOM FUNCTION-----------------------------------

#-------------------------------MASTER BEDROOM FUNCTION-----------------------------------------
def master_bedroom():
    
    # Setup GPIO pins
    light_pin = 18
    fan_pin = 23
    ac_pin = 24

    # Set up DHT11 sensor
    DHT11_PIN = 25

    # Set up Window and door
    window_pin = 11
    door_pin = 16

    # Initialize GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(light_pin, GPIO.OUT)
    GPIO.setup(fan_pin, GPIO.OUT)
    GPIO.setup(ac_pin, GPIO.OUT)
    GPIO.setup(door_pin, GPIO.OUT)
    GPIO.setup(window_pin, GPIO.OUT)
    dht_device = adafruit_dht.DHT11(board.D4)


    # Read data from DHT11 sensor
    def read_dht11_data():
        while True:
            try:
                temperature_c = dht_device.temperature
                temperature_f = temperature_c*(9 / 5) + 32
                humidity = dht_device.humidity
                print("Temp:{:.1f} C / {:.1f} F    Humidity: {}%".format(temperature_c, temperature_f, humidity))
            except RuntimeError as err:
                print(err.args[0])

            time.sleep(1)

    # Light status management
    def light_status(status):
        if status == 'on':
            GPIO.output(light_pin, GPIO.HIGH)
        elif status == 'off':
            GPIO.output(light_pin, GPIO.LOW)

    # Fan status management
    def fan_status(status):
        if status == 'on':
            GPIO.output(fan_pin, GPIO.HIGH)
        elif status == 'off':
            GPIO.output(fan_pin, GPIO.LOW)

    # AC status management
    def ac_status(status):
        if status == 'on':
            GPIO.output(ac_pin, GPIO.HIGH)
        elif status == 'off':
            GPIO.output(ac_pin, GPIO.LOW)

    # Function to get status of the door
    def door_status():
        if status == 'open':
            GPIO.input(door_pin, GPIO.HIGH)
        elif status == 'closed':
            GPIO.input(door_pin, GPIO.LOW)
        

    # Function to get status of the window
    def window_status():
        if status == 'open':
            GPIO.input(window_pin, GPIO.HIGH)
        elif status == 'closed':
            GPIO.input(window_pin, GPIO.LOW)
 
    def read_image(master_bedroom):
        #filename = 'uploads\\123.jpg'
        #---------------or---------------
        """image_path = f'uploads/{pid}.jpg'  # Adjust the path based on your file structure
        try:
            with open(image_path, 'rb') as image_file:
                return image_file.read()
        except FileNotFoundError:
            return None
        """
        #---------------or----------------
        image_url = f'https://res.cloudinary.com/dmfwpz555/image/upload/rooms/master_bedroom.jpg'  # Replace with the actual URL

        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            return response.content
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as err:
            print(f"Error: {err}")
            return None
        # Implement this function to read the image file based on the provided PID
        # Example: Read image from file system or database
        # Return image data as bytes or None if PID is invalid
    

    @app.route('/images/master_bedroom.jpg', methods=['GET'])
    def get_image(master_bedroom):
        image_binary = read_image(master_bedroom)
        response = make_response(image_binary)
        response.headers.set('Content-Type', 'image/jpeg')
        response.headers.set(
            'Content-Disposition', 'attachment', filename='%s.jpg' % master_bedroom)
        return response, send_file(
        io.BytesIO(image_binary),
        mimetype='image/jpeg',
        as_attachment=True,
        download_name='%s.jpg' % master_bedroom)
    
     # Create the /status endpoint
    @app.route('/api/status', methods=['GET'])
    def status():
        light = GPIO.input(light_pin)
        fan = GPIO.input(fan_pin)
        ac = GPIO.input(ac_pin)
        dh11_data = read_dht11_data()
        door = door_status()
        window = window_status()

        status = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'light': 'on' if light == GPIO.HIGH else 'off',
            'fan': 'on' if fan == GPIO.HIGH else 'off',
            'ac': 'on' if ac == GPIO.HIGH else 'off',
            'temperature': dh11_data['temperature'],
            'humidity': dh11_data['humidity'],
            'door_status': 'open' if door == GPIO.HIGH else 'closed',
            'window': 'open' if window == GPIO.HIGH else 'closed',
        }
    
        return jsonify(status)

    # Define a route to handle GET requests for counting active devices
    @app.route('/api/device_count', methods=['GET'])
    def device_count():
        devices = {
            'light': GPIO.input(light_pin),
            'fan': GPIO.input(fan_pin),
            'ac': GPIO.input(ac_pin),
            'door': GPIO.input(door_pin),
            'window': GPIO.input(window_pin),
        }

        active_devices = sum(devices.values())

        return jsonify({'active_devices': active_devices})

    # Define a route to handle POST requests for controlling the devices
    @app.route('/api/control', methods=['POST'])
    def control_devices():
        req_data = request.get_json()

        if 'devices' in req_data:
            devices = req_data['devices']

            for device_name, status in devices.items():
                if device_name == 'light':
                    light_status(status)
                elif device_name == 'fan':
                    fan_status(status)
                elif device_name == 'ac':
                    ac_status(status)
                elif device_name == 'door':
                    door_status(status)
                    # Update the door status after setting its value
                    status_dict = {'door_status': 'open' if GPIO.input(door_pin) else 'closed'}
                elif device_name == 'window':
                    window_status(status)
                    # Update the window status after setting its value
                    status_dict = {'window': 'open' if GPIO.input(window_pin) else 'closed'}

                if device_name in ['light', 'fan', 'ac']:
                    # Update the status of the controllable device
                    status_dict[device_name] = 'on' if status == 'true' else 'off'

            # Return the updated status in the response
            return jsonify(status_dict)

        else:
            return jsonify({'error': 'No devices specified in the request'}), 400

    
#--------------------------END OF MASTER BEDROOM FUNCTION-----------------------------------
# Define a dictionary to store modes
rooms = {
    'Living room': 'Turns off all the appliances,locks all windows, doors and gates',
    'Kitchen': 'Turns on ambient lights, a mood setter',
    'Guest room': 'Monitor and track guest movements to provide them hospitality',
    'Child and Elder room': 'Monitor and track movements to provide them supervision',
    'Bedroom': 'Enable emergency and evacuation protocols',
}

# Define a route to handle GET requests
@app.route('/api/data', methods=['GET'])
def get_rooms():
    selected_room = request.args.get('room')
    if selected_room:
        main(selected_room)
    return jsonify(rooms)

def main(selected_room):
    # Implement the logic for each room here
    if selected_room == 'Living room':
        living_room()
        print('Living room enabled')
    if selected_room == 'Kitchen':
        kitchen()
        print(' Kitchen enabled')
    if selected_room == 'Guest room':
        guest_bedroom()
        print('Guest room enabled')
    if selected_room == 'Children bedroom':
        children_bedroom()
        print('Children bedroom enabled')
    if selected_room == 'Master bedroom':
        master_bedroom()
        print('Master bedroom enabled')


if __name__ == '__main__':
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(light_pin, GPIO.OUT)
        GPIO.setup(fan_pin, GPIO.OUT)
        GPIO.setup(ac_pin, GPIO.OUT)
        GPIO.setup(door_pin, GPIO.OUT)
        GPIO.setup(window_pin, GPIO.OUT)
        app.run(debug=True, host='0.0.0.0', port=8000)
        #or
        """if __name__ == '__main__':
            try:
                GPIO.setmode(GPIO.BCM)
                light_pin, fan_pin, ac_pin, DHT11_PIN, door_pin, window_pin = 18, 23, 24, 25, 11, 16
                app.run(debug=True, host='0.0.0.0', port=8000)
            except KeyboardInterrupt:
                print("Program interrupted with keyboard")
            finally:
                GPIO.cleanup()"""

