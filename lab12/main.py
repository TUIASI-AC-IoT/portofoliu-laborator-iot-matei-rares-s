import json
import os
import uuid
import random
from flask import *
app = Flask(__name__)

app.config['DEBUG'] = True
CONFIG_DIR = "configs"

SIMULATED_SENSORS = {
    "temp": lambda: round(random.uniform(20.0, 30.0), 2),
    "humidity": lambda: round(random.uniform(40.0, 60.0), 2),
    "pressure": lambda: round(random.uniform(990.0, 1020.0), 2)
}

os.makedirs(CONFIG_DIR, exist_ok=True)

@app.route('/sensor/<sensor_id>', methods=['GET'])
def read_sensor(sensor_id):
    if sensor_id not in SIMULATED_SENSORS:
        abort(404, description=f"Senzorul '{sensor_id}' nu există.")

    value = SIMULATED_SENSORS[sensor_id]()
    return jsonify({
        "value": value
    })

@app.route('/sensor/<sensor_id>', methods=['POST'])
def create_config(sensor_id):
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
        "details": f"Fișierul creat.",
    }), 201


@app.route('/sensor/<sensor_id>', methods=['PUT'])
def update_config(sensor_id):
    config_path = os.path.join(CONFIG_DIR, f'{sensor_id}.json')

    if not os.path.exists(config_path):
        return jsonify({
            "details": f"Nu se poate actualiza fișierul pentru senzorul '{sensor_id}' deoarece nu exista."
        }), 400

    config_data = request.get_json()

    with open(config_path, 'w') as f:
        json.dump(config_data, f)

    return jsonify({
        "details": f"Fișierul de configurare pentru {sensor_id}.json a fost actualizat.",
    })

if __name__ == '__main__':
    app.run()

