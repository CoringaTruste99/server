from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

CONFIG_FILE = "servo_config.json"

# Inicializa archivo de configuración si no existe
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as f:
        json.dump({
            "activar_servo": False,
            "intervalo_minutos": 30,
            "temporizador_activo": True
        }, f)

# Cargar configuración desde archivo
def cargar_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

# Guardar configuración al archivo
def guardar_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

# Ruta GET usada por el ESP32 para leer si debe activar el servo
@app.route("/get_servo_config", methods=["GET"])
def get_servo_config():
    try:
        config = cargar_config()
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta POST usada por el ESP32 para resetear el flag después de activarse
@app.route("/reset_servo_flag", methods=["POST"])
def reset_servo_flag():
    try:
        config = cargar_config()
        config["activar_servo"] = False  # Resetea el flag
        guardar_config(config)
        return jsonify({"status": "flag_reset_ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta POST usada por la app Expo para cambiar intervalo y/o activar manualmente el servo
@app.route("/set_servo_config", methods=["POST"])
def set_servo_config():
    try:
        data = request.get_json()
        config = cargar_config()

        # Cambiar temporizador si se manda explícitamente
        if "temporizador_activo" in data:
            config["temporizador_activo"] = bool(data["temporizador_activo"])

        # Cambiar intervalo si se envía
        if "intervalo_minutos" in data:
            intervalo = float(data["intervalo_minutos"])
            if 0 <= intervalo <= 999:
                config["intervalo_minutos"] = intervalo

        # Activación manual
        if "activar_servo" in data and data["activar_servo"]:
            config["activar_servo"] = True  # Se activa una vez

        guardar_config(config)
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
