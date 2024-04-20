from flask import Flask, request, make_response, jsonify
import RPi.GPIO as GPIO

app = Flask(__name__)

app.secret_key = 'king'

#-------------------------------INITIALIZE ALL DEVICES WITH GPIO-----------------------------------------

# Initialize GPIO
def init_GPIO_board():
    # define all gpio pins
    test_light = 16
    test_fan = 15
    
    # Set up GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    GPIO.setup(test_light, GPIO.OUT)
    GPIO.setup(test_fan, GPIO.OUT)


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
                "gpio": 30,
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
                "gpio": 31,
            },
            {
                "name": "Fan",
                "icon": "mdi-fan",
                "status": "false",
                "gpio": 15,
            },
            {
                "name": "AC",
                "icon": "mdi-air-conditioner",
                "status": "false",
                "gpio": 33,
            }
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
                "gpio": 34,
            },
            {
                "name": "Fan",
                "icon": "mdi-fan",
                "status": "false",
                "gpio": 35,
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
            }
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


# -----------------------------------------------------------------------


# -- update a device
@app.route('/update-device', methods=['POST'])
def update_device_status():
    post_request_body = request.get_json()
    room_number = post_request_body.get('room')
    update_device = post_request_body.get('update_device')
        
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
        
        
        ###############################################

        return jsonify({"success": "device status updated"}), 200

    except:
        return jsonify({"error": "Invalid request"}), 400
        
    '''if isinstance(room_number, int) and update_device:
        room = next((r for r in all_rooms_detailed if r['room_name'] == str(room_number)), None)
        if room:
            device_index = update_device[0]
            device_status = update_device[1]
            if 0 <= device_index < len(room['devices']):
                room['devices'][device_index]['status'] = device_status
                response_body = {
                    "room": room_number,
                    "img": room["image_url"],
                    "avail_devices": [
                        [device["name"], device["icon"], device["status"]]
                        for device in room["devices"]
                    ]
                }
                return jsonify(response_body), 200
            else:
                return jsonify({"error": "Invalid device index"}), 400
        else:
            return jsonify({"error": "Room not found"}), 404
    else:
        return jsonify({"error": "Invalid request"}), 400'''
    

#------------------------------- -----------------------------------------

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
                pass        # delete pass after GPIO code done
            elif new_mode == "Saver":
                # create and call function to update devices
                pass        # delete pass after GPIO code done
            elif new_mode == "Vacay":
                # create and call function to update devices
                pass        # delete pass after GPIO code done
            
            print(new_mode)
            return jsonify({"succes": "Mode updated"}), 200
        else:
            return jsonify({"error": "Failed to update mode"}), 404

    
    except:
        return jsonify({"error": "Failed to update mode"}), 404

#------------------------------- -----------------------------------------

# clean up
@app.route('/exit')
def exit_clean_gpio():
    GPIO.cleanup()
    return jsonify({"msg": "GPIO cleaned"}), 200


if __name__ == '__main__':
    init_GPIO_board()
    app.run(debug=True, host='0.0.0.0')