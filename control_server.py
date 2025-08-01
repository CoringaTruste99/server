from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Thread
import time

app = Flask(__name__)
CORS(app)

# Estado actual del temporizador y control manual
config = {
    "intervalo_minutos": 30,
    "activar_servo": False
}

ultimo_activado = 0  # Timestamp del último disparo

@app.route("/config", methods=["POST"])
def configurar():
    global ultimo_activado
    data = request.get_json()
    intervalo = data.get("intervalo_minutos")
    activar = data.get("activar_servo")

    if intervalo is not None:
        config["intervalo_minutos"] = intervalo
    if activar is not None:
        config["activar_servo"] = activar
        if activar == False:
            ultimo_activado = time.time()

    return jsonify({"status": "config_actualizada", "config": config}), 200

@app.route("/config", methods=["GET"])
def obtener_config():
    return jsonify(config), 200

@app.route("/activar", methods=["POST"])
def activar_servo_manual():
    config["activar_servo"] = True
    return jsonify({"status": "servo_activado"}), 200

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "online"}), 200

def loop_control():
    global ultimo_activado
    while True:
        time.sleep(5)
        ahora = time.time()
        intervalo_segundos = config["intervalo_minutos"] * 60
        if ahora - ultimo_activado >= intervalo_segundos:
            config["activar_servo"] = True
            ultimo_activado = ahora

# Ejecutar thread en segundo plano
Thread(target=loop_control, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
