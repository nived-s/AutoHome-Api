from flask import Flask, request, make_response, jsonify
from piservo import Servo
import RPi.GPIO as GPIO

import adafruit_dht
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio

import sqlite3
import hashlib
import re


app = Flask(__name__)

app.secret_key = 'king'

#-------------------------------INITIALIZE ALL DEVICES WITH GPIO-----------------------------------------

# servo motor
garage_servo = Servo(12)
hall_servo = Servo(13)

# Initialize GPIO
def init_GPIO_board():
    # define all gpio pins
    living_room_light = 16
    living_room_ac = 20
    living_room_door = 50
    
    master_bedroom_light = 18
    master_bedroom_fan = 26
    
    child_bedroom_light = 25
    child_bedroom_ac = 25
    
    kitchen_light = 51
    
    garage_light = 52
    garage_door = 53
    
    DHT11_PIN = 25
    
    ir_sensor_pin = 23
    
     
    
    # Set up GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(living_room_light, GPIO.OUT)
    GPIO.setup(living_room_ac, GPIO.OUT)
    GPIO.setup(living_room_door, GPIO.OUT)
    
    GPIO.setup(master_bedroom_light, GPIO.OUT)
    GPIO.setup(master_bedroom_fan, GPIO.OUT)
    
    GPIO.setup(child_bedroom_light, GPIO.OUT)
    GPIO.setup(child_bedroom_ac, GPIO.OUT)
    
    GPIO.setup(kitchen_light, GPIO.OUT)
    
    GPIO.setup(garage_light, GPIO.OUT)
    GPIO.setup(garage_door, GPIO.OUT)
    
    GPIO.setup(ir_sensor_pin, GPIO.OUT)


#------------------------------- -----------------------------------------

#-------------------------------ALL ROOMS GET {{ ROOMS PAGE }}-----------------------------------------

all_rooms_small = [
    {
        "room_name": "Living Room",
        "image_url": "https://res.cloudinary.com/dmfwpz555/image/upload/rooms/hall.jpg",
        "avail_devices": 4
    },
    {
        "room_name": "Kitchen",
        "image_url": "https://res.cloudinary.com/dmfwpz555/image/upload/rooms/kitchen.jpg",
        "avail_devices": 5
    },
    {
        "room_name": "Master Bedroom",
        "image_url": "https://res.cloudinary.com/dmfwpz555/image/upload/rooms/master_bedroom.jpg",
        "avail_devices": 3
    },
    {
        "room_name": "Children Bedroom",
        "image_url": "https://res.cloudinary.com/dmfwpz555/image/upload/rooms/children_bedroom.jpg",
        "avail_devices": 1
    },
    {
        "room_name": "Guest Bedroom",
        "image_url": "https://res.cloudinary.com/dmfwpz555/image/upload/rooms/guest_room.jpg",
        "avail_devices": 2
    }
]

@app.route('/all-rooms', methods=['GET'])
def get_rooms():
    return jsonify(all_rooms_small)

#------------------------------- -----------------------------------------

#-------------------------------INDIVIDUAL ROOM POST {{ ROOMS PAGE }}-----------------------------------------

''' 
Each room will have different response according to request body..
-Room is identified by the index from the all_rooms list
    post_request_body = {
        room : 2
    }
    
    here room=2, so Master bedroom is refered.
    
-In the response body of request, 
    response_body = {
        room : 2,
        img : "url of image"
        avail_devices = {
            [ fan , 'fan_icon' , true(is on or off)],
            [ light , 'light_icon' , false]
        }
    }
    
    in the flutter app, room num(here 2) is saved. 
    
-To update status of any device(POST)
    req_body = {
        room : 2,
        update_device : [ 0, false ]
    }
    
    above eg. shows updation of fan(which is index 0 of room 2) to false state.

'''

all_rooms_detailed = [
    {
        "room_name": "Kitchen",
        "image_url": "https://res.cloudinary.com/dmfwpz555/image/upload/rooms/kitchen.jpg",
        "devices": [
            {
                "name": "Light",
                "icon": "mdi-ceiling-light",
                "status": "false",
                "gpio": 16,
            },
        ]
    },
    {
        "room_name": "Hall",
        "image_url": "https://res.cloudinary.com/dmfwpz555/image/upload/rooms/hall.jpg",
        "devices": [
            {
                "name": "AC",
                "icon": "mdi-air-conditioner",
                "status": "false",
                "gpio": 29,
            },
            {
                "name": "Light",
                "icon": "mdi-ceiling-light",
                "status": "false",
                "gpio": 20,
            },
            {
                "name": "Door",
                "icon": "mdi-glassdoor",
                "status": "false",
                "gpio": 13,
            },
        ]
    },
    
    {
        "room_name": "Master Bedroom",
        "image_url": "https://res.cloudinary.com/dmfwpz555/image/upload/rooms/master_bedroom.jpg",
        "devices": [
            {
                "name": "Light",
                "icon": "mdi-ceiling-light",
                 "status": "false",
                "gpio": 18,
            },
            {
                "name": "Fan",
                "icon": "mdi-fan",
                "status": "false",
                "gpio": 15,
            },
        ]
    },
    {
        "room_name": "Children Bedroom",
        "image_url": "https://res.cloudinary.com/dmfwpz555/image/upload/rooms/children_bedroom.jpg",
        "devices": [
            {
                "name": "Light",
                "icon": "mdi-ceiling-light",
                "status": "false",
                "gpio": 25,
            },
            {
                "name": "AC",
                "icon": "mdi-air-conditioner",
                "status": "false",
                "gpio": 36,
            }
        ]
    },
    {
        "room_name": "Garage",
        "image_url": "https://res.cloudinary.com/dmfwpz555/image/upload/rooms/guest_room.jpg",
        "devices": [
            {
                "name": "Light",
                "icon": "mdi-ceiling-light",
                "status": "false",
                "gpio": 37,
            },
            {
                "name": "Door",
                "icon": "mdi-glassdoor",
                "status": "false",
                "gpio": 12,
            },
        ]
    }
]

# -- respond avail devices
@app.route('/individual-room', methods=['POST'])
def get_room_devices():
    post_request_body = request.get_json()
    room_number = post_request_body.get('room')
        
    try:
        response_body = {
                "room": room_number,
                "img": all_rooms_detailed[room_number]['image_url'],
                "avail_devices": [
                    [device["name"], device["icon"], device["status"], device["gpio"]]
                    for device in all_rooms_detailed[room_number]["devices"]
                ]
            }
        return jsonify(response_body), 200
    except:
        return jsonify({"error": "Room not found"}), 404
    
# -----------------------------------------------------------------------

# -- update LED Device

# ON LED
def on_LED(device_gpio):
    # set light to HIGH
    GPIO.output(device_gpio, GPIO.HIGH)

    print("Status is true of ", device_gpio)
    

# OFF LED
def off_LED(device_gpio):
    # set light to LOW
    GPIO.output(device_gpio, GPIO.LOW)

    print("Status is false of ", device_gpio)


# -- update FAN Device

# ON FAN
def on_FAN(device_gpio):
    # set light to HIGH
    GPIO.output(device_gpio, GPIO.HIGH)

    print("Status is true of", device_gpio)
    

# OFF FAN
def off_FAN(device_gpio):
    # set light to LOW
    GPIO.output(device_gpio, GPIO.LOW)

    print("Status is false of ", device_gpio)
 
# -- update DOOR Device

# ON DOOR   
def on_DOOR(device_gpio):
    """Rotate servo from 0 to 90 degree."""
    # garage
    if device_gpio == 12:
        garage_servo.write(0)
        time.sleep(1)
        garage_servo.write(90)
        time.sleep(1)
    
    # living room
    if device_gpio == 13:
        hall_servo.write(0)
        time.sleep(1)
        hall_servo.write(90)
        time.sleep(1)

# OFF DOOR
def off_DOOR(device_gpio):
    """Rotate servo from 90 to 0 degree."""
    # garage
    if device_gpio == 12:
        garage_servo.write(90)
        time.sleep(1)
        garage_servo.write(0)
        time.sleep(1)
        
    # living room
    if device_gpio == 13:
        hall_servo.write(90)
        time.sleep(1)
        hall_servo.write(0)
        time.sleep(1)

# -----------------------------------------------------------------------

# -- update a device
@app.route('/update-device', methods=['POST'])
def update_device_status():
    post_request_body = request.get_json()
    room_number = post_request_body.get('room')
    update_device = post_request_body.get('update_device')
    
    print(room_number, update_device)
        
    try:
        device_index = update_device[0]
        device_status = update_device[1]
        device_gpio = update_device[2]
        
        # updating all_rooms_details list
        all_rooms_detailed[room_number]['devices'][device_index]['status'] = device_status
       
        to_update_device = all_rooms_detailed[room_number]['devices'][device_index]['name']
        
        ## update from GPIO code
        if to_update_device in ['AC', 'Light']:
            if device_status.lower() == 'true':
                on_LED(device_gpio) 
                
            elif device_status.lower() == 'false':
                off_LED(device_gpio)
            
            else:
                return jsonify({'error': 'Invalid status value. Must be "true" or "false".'}), 400
        
        if to_update_device in ['Fan']:
            if device_status.lower() == 'true':
                on_FAN(device_gpio) 
                
            elif device_status.lower() == 'false':
                off_FAN(device_gpio)
            
            else:
                return jsonify({'error': 'Invalid status value. Must be "true" or "false".'}), 400
        
        if to_update_device in ['Door']:
            if device_status.lower() == 'true':
                on_DOOR(device_gpio)
                
            elif device_status.lower() == 'false':
                off_DOOR(device_gpio)
            
            else:
                return jsonify({'error': 'Invalid status value. Must be "true" or "false".'}), 400
        
        
        ###############################################

        return jsonify({"success": "device status updated"}), 200

    except:
        return jsonify({"error": "Invalid request"}), 400
    
    
#------------------------------- -----------------------------------------

#---------------------------smoke detection-------------------------------
# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# Define the LDR and MQ-7 sensor channels
mq7_channel = AnalogIn(ads, ADS.P1)

# Define the conversion factor for the ADC (mV per bit)
conversion_factor = 3.0 / 32768.0

# Define the lookup table for the MQ-7 sensor
mq7_lut = [
    0, 50, 100, 200, 500, 1000, 2000, 5000, 10000
]

def read_sensors():

  mq7_value = read_channel(mq7_channel)
  mq7_ppm = read_mq7(mq7_value)

  return mq7_ppm

def read_channel(channel):
  value = channel.value
  voltage = value * conversion_factor * 6.144
  return voltage

def read_mq7(value):
  closest = min(range(len(mq7_lut)), key=lambda i: abs(mq7_lut[i]-value))
  return mq7_lut[closest]

def detect_smoke():
    closest = min(range(len(mq7_lut)), key=lambda i: abs(mq7_lut[i]-value))
    mq7_value = read_channel(mq7_channel)
    mq7_ppm = read_mq7(mq7_value)
    #mq2_sensor = MQ2Sensor()  # Initialize the MQ2 sensor
    #smoke_ppm = mq2_sensor.read_ppm()  # Read smoke concentration in ppm
    print("MQ-7 value: {:.2f} ppm".format(mq7_ppm))
    time.sleep(1)

    # Activate buzzer and red LED if smoke concentration is above 200 ppm
    if mq7_ppm > 200:
        sendOrNot = send_alert_to_home()
        
        if sendOrNot:
            print("successfully send notification")
        else:
            print("Failed to send notification")

    # Define severity levels based on ppm ranges
    if mq7_ppm < 200:
        severity = "Low"
    elif 200 <= smoke_ppm < 700:
        severity = "Moderately High"
    elif 700 <= smoke_ppm < 4000:
        severity = "High"
    else:
        severity = "Dangerous"

    return mq7_ppm, severity, mq7_lut[closest]

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
    
    
def send_alert_to_home():
    try:
        data = {
            "to": "eSWeRvWhTN2fXtSYmoRG52:APA91bFeF29mb13Z88RzjPDJpZEddQ1FXRwVVok3Dr3-id_itbEyAoanEjjZkUvle80B1l3_UJeKt5UWWCUU3_BYGi8mFHi-BR7G1VfRzfWM3YI7BCxQ3lLmOOXxwcFy_SLMonvXbTCK",
            "notification": {
                "title": "Smoke Alert",
                "body": "Smoke detected!"
            }
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": "key=AAAAwv7aN9s:APA91bHn5Yj8ZqE7MDRjCl1LCpTXKHWrTKTS10hy-AszzbInvCyg0NzA7HIokBtat5sTDwCtSF2HHyIaX2cR1F7RS7KY5p1ZTuz8Jb1iYYJSCSZlGiag3IP8MKKoDmu1DiDAgDqvOkyt"
        }
        requests.post("https://fcm.googleapis.com/fcm/send",
                    json=data, headers=headers)
        return True
    except:
        return False

    #######################------------------in the main function----------------------------------
# def main():
#     while True:
#         # Detect smoke and determine severity
#         mq7_ppm, severity = detect_smoke()
#         time.sleep(300)  # Check for smoke every 5 minutes
        
        
#------------------------------- -----------------------------------------        


#---------------------------smoke detection-------------------------------


@app.route('/sensor_data', methods=['GET'])
def read_dht11_data():
    try:
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT11_PIN)
        if humidity is not None and temperature is not None:
            result = {'temperature': temperature, 'humidity': humidity}
        else:
            result = {'temperature': None, 'humidity': None}
    except Exception as e:
        # Handle sensor reading errors (optional)
        result = {'error': str(e)}

    return jsonify(result)

#---------------------------movement detection door open-------------------------------
def check_for_movement():
    if GPIO.input(23):
        print('movement detected')
        on_DOOR(12)
        time.sleep(100)
        off_DOOR(12)


#-------------------------------Modes and desciption {{ MODES PAGE }}-----------------------------------------


selected_mode = 'Away'

# Define a dictionary to store modes
modes_detailed = {
    'Away': 'Turns off all the appliances,locks all windows, doors and gates',
    'Ambient': 'Turns on ambient lights, a mood setter',
    'Guest': 'Monitor and track guest movements to provide them hospitality',
    'Child and Elder': 'Monitor and track movements to provide them supervision',
    'Emergency': 'Enable emergency and evacuation protocols',
    'Night': 'Prepare for a restful night and sound sleep',
    'Energy Saver': 'Save application from overusage and reduce electricity bill',
    'Vacay': 'Turns off all the appliances, locks all windows, doors and gates, ensuring safety for a long leave from home',
}

modes_small = {
    "Away": 'True',
    "Ambient": 'True',
    "Child and Elder": 'True',
    "Emergency": 'True',
    "Energy Saver": 'True',
    "Guest": 'True',
    "Night": 'True',
    "Vacay": 'True'
}

# -- show all modes GET
@app.route('/all-modes', methods=['GET'])
def get_modes():
    responseBody = {
        "details" : modes_detailed,
        "mode": selected_mode,
    }
    
    return jsonify(responseBody)

@app.route('/all-modes-small', methods=['GET'])
def get_modes_small():
    responseBody = {
        "details" : modes_small,
        "mode": selected_mode,
    }
    return jsonify(responseBody)


# -- update mode POST
@app.route('/update-mode', methods=['POST'])
def update_mode():
    global selected_mode
    post_request_body = request.get_json()
    new_mode = post_request_body.get('mode')
    
    # List of modes
    modes = [
        'Away',
        'Ambient',
        'Guest',
        'Children',
        'Emergency',
        'Night',
        'Saver',
        'Vacay',
    ]
    
    try:
        if new_mode in modes:
            selected_mode = new_mode
            
            if new_mode == "Away":
                # create and call function to update devices
            
                """
                close door and window
                close all appliances inside(light, fan, ac)
                """
                
                try:
                    off_DOOR(12)
                    off_DOOR(13)
                
                except:
                    print('failed to update')
                    return jsonify({"error": "Failed to update away mode"}), 404
                
                pass        # delete pass after GPIO code done
            elif new_mode == "Ambient":
                # create and call function to update devices
                pass        # delete pass after GPIO code done
            elif new_mode == "Guest":
                # create and call function to update devices
                pass        # delete pass after GPIO code done
            elif new_mode == "Children":
                # create and call function to update devices
                pass        # delete pass after GPIO code done
            elif new_mode == "Emergency":
                # create and call function to update devices
                pass        # delete pass after GPIO code done
            elif new_mode == "Night":
                # create and call function to update devices
                
                """
                close door and window
                close all appliances inside(light, fan, ac)
                open outside light
                """
                
                pass        # delete pass after GPIO code done
            elif new_mode == "Saver":
                # create and call function to update devices
                
                """
                close ac
                """
                
                pass        # delete pass after GPIO code done
            elif new_mode == "Vacay":
                # create and call function to update devices
            
                """
                close door and window
                close all appliances inside(light, fan, ac)
                """
            
                pass        # delete pass after GPIO code done
            
            
            print(new_mode)
            return jsonify({"succes": "Mode updated"}), 200
        else:
            return jsonify({"error": "Failed to update mode"}), 404

    
    except:
        return jsonify({"error": "Failed to update mode"}), 404

#------------------------------- -----------------------------------------


#------------------------------- Login And Signup -----------------------------------------

email_condition = "^[a-z]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Connect to the database
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    # Check if the provided username and password match any user record in the database
    cursor.execute("SELECT * FROM USERS WHERE USERNAME = ? AND PASSWORD = ?", (username, hashlib.sha512(password.encode()).hexdigest()))
    user = cursor.fetchone()

    conn.close()

    if user:
        return jsonify({'message': 'Login successful!'}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 500

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if password != confirm_password:
        return jsonify({'message': 'Password and confirm password do not match!'}), 500

    if not re.search(email_condition, email):
        return jsonify({'message': 'Invalid email format!'}), 500

    # Connect to the database
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    # Check if username already exists
    cursor.execute("SELECT * FROM USERS WHERE USERNAME = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'message': 'Username already exists!'}), 500

    # Insert new user data into the database
    cursor.execute("INSERT INTO USERS (USERNAME, EMAIL, PASSWORD) VALUES (?, ?, ?)", (username, email, hashlib.sha512(password.encode()).hexdigest()))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User registered successfully!'}), 200

#------------------------------- -----------------------------------------


# clean up
@app.route('/exit')
def exit_clean_gpio():
    GPIO.cleanup()
    return jsonify({"msg": "GPIO cleaned"}), 200


if __name__ == '__main__':
    init_GPIO_board()
    app.run(debug=True, host='0.0.0.0')
    
    while True:
        # Detect smoke and determine severity
        # mq7_ppm, severity = detect_smoke()
        # time.sleep(300)  # Check for smoke every 5 minutes
        check_for_movement()
    