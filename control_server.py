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

# Ruta única para manejar toda la configuración
@app.route("/config", methods=["GET", "POST"])
def handle_config():
    try:
        config = cargar_config()
        
        if request.method == "GET":
            return jsonify(config)
            
        elif request.method == "POST":
            data = request.get_json()
            
            # Actualizar solo los campos proporcionados
            if "intervalo_minutos" in data:
                intervalo = float(data["intervalo_minutos"])
                if 0 <= intervalo <= 999:
                    config["intervalo_minutos"] = intervalo
                    
            if "temporizador_activo" in data:
                config["temporizador_activo"] = bool(data["temporizador_activo"])
                
            if "activar_servo" in data:
                config["activar_servo"] = bool(data["activar_servo"])
            
            guardar_config(config)
            return jsonify(config)
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)