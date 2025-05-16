import json
import os
import uuid
import random
from datetime import datetime, timedelta

from firebase_admin.exceptions import NOT_FOUND
from flask import *
from flask import Flask, request, g, jsonify
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

app = Flask(__name__)

app.config['DEBUG'] = True
CONFIG_DIR = "configs"
app.config['SECRET_KEY'] = 'supersecretkey'

SIMULATED_SENSORS = {
    "temp": lambda: round(random.uniform(20.0, 30.0), 2),
    "humidity": lambda: round(random.uniform(40.0, 60.0), 2),
    "pressure": lambda: round(random.uniform(990.0, 1020.0), 2)
}
ROLES = {'guest', 'owner', 'admin'}

os.makedirs(CONFIG_DIR, exist_ok=True)

@app.before_request
def check_token():
    token = request.headers.get('Authorization')
    g.user_role = 'guest'
    if token:
        verify_token()

USERS = {
    "admin": {"password": "admin", "role": "admin"},
    "owner": {"password": "owner", "role": "owner"},
}

@app.route('/auth', methods=['POST'])
def auth():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password are required."}), 400

    username = data['username']
    password = data['password']

    user = USERS.get(username)

    if not user or user['password'] != password:
        return jsonify({"error": "Invalid username or password."}), 401

    role = user['role']

    payload = {
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({
        "role": role,
        "token": token
    })


payload = None
@app.route('/auth/jwtStore', methods=['GET'])
def verify_token():
    auth_header = request.headers.get('Authorization')
    print(auth_header)
    if not auth_header:
        return jsonify({"error": "Authorization header missing."}), 401

    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return jsonify({"error": "Authorization header must be in format: Bearer <token>."}), 400

    token = parts[1]

    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        print(payload)
        g.user_role = payload.get('role')
        return jsonify({
            "message": "Token is valid."
        })
    except Exception as e:
        return jsonify({"error": "Invalid token.", "details": str(e)}), 401

@app.route('/auth/jwtStore', methods=['DELETE'])
def delete_resource():
    verify_token()

    #delete from database
    NOT_FOUND = 1
    DATABASE = [2,3,4]
    if NOT_FOUND in DATABASE:
        return jsonify({
            "error": "Resource not found.",
        }), 404

    return jsonify({
        "message": "Resource deleted successfully.",
    }), 200


@app.route('/sensor/<sensor_id>', methods=['GET'])
def read_sensor(sensor_id):
    if g.user_role == 'guest':
        print("inquest")
        return jsonify({
            "details": "Nu ai permisiunea de a accesa aceasta resursa.",
            "auth":{"url":"http://127.0.0.1:5000/auth", "method":"POST",}
        }), 403


    if sensor_id not in SIMULATED_SENSORS:
        abort(404, description=f"Senzorul '{sensor_id}' nu exista")

    value = SIMULATED_SENSORS[sensor_id]()
    return jsonify({
        "value": value
    })

@app.route('/sensor/<sensor_id>', methods=['POST'])
def create_config(sensor_id):
    if g.user_role != 'admin':
        return jsonify({
            "details": "Nu ai permisiunea de a accesa aceasta resursa.",
                       "auth":{"url": "http://127.0.0.1:5000/auth", "method": "POST", }
        }), 403

    config_path = os.path.join(CONFIG_DIR, f"{sensor_id}.json")

    if os.path.exists(config_path):
        return jsonify({
            "details": f"Fisierul pentru senzorul '{sensor_id}' exista deja."
        }), 409

    try:
        config_data = request.get_json(force=True)
    except Exception:
        return jsonify({
            "details": "Cererea nu conține un JSON valid, datele trebuie sa fie în format application/json."
        }), 406

    scale = config_data.get("scale", 1.0)

    scale = float(scale)
    if scale <= 0:
        return jsonify({
                "details": "Yo, your field 'scale' needs to be positive."
            }), 400

    config_data["scale"] = scale
    with open(config_path, 'w') as f:
        json.dump(config_data, f)

    return jsonify({
        "details": f"Fisierul creat.",
    }), 201


@app.route('/sensor/<sensor_id>', methods=['PUT'])
def update_config(sensor_id):
    if g.user_role != 'admin':
        return jsonify({
            "details": "Nu ai permisiunea de a accesa aceasta resursa.",
            "auth": {"url": "http://127.0.0.1:5000/auth", "method": "POST", }
        }), 403

    config_path = os.path.join(CONFIG_DIR, f'{sensor_id}.json')

    if not os.path.exists(config_path):
        return jsonify({
            "details": f"Nu se poate actualiza fișierul pentru senzorul '{sensor_id}' deoarece nu exista."
        }), 400

    config_data = request.get_json()

    with open(config_path, 'w') as f:
        json.dump(config_data, f)

    return jsonify({
        "details": f"Fisierul de configurare pentru {sensor_id}.json a fost actualizat.",
    })

if __name__ == '__main__':
    app.run()

