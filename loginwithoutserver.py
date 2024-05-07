
from flask import Flask, request, jsonify
import sqlite3
import hashlib
import re

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)
