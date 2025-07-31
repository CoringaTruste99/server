from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Estado global (en producción usar base de datos o Redis)
estado = {
    "servo_activado": False,
    "ultimo_activado": None,
    "temporizador_segundos": 60  # por defecto 60 segundos
}

@app.route("/api/activar_servo", methods=["POST"])
def activar_servo():
    global estado
    estado["servo_activado"] = True
    estado["ultimo_activado"] = datetime.now()
    return jsonify({"status": "servo activado"}), 200

@app.route("/api/set_temporizador", methods=["POST"])
def set_temporizador():
    global estado
    data = request.json
    if not data or "segundos" not in data:
        return jsonify({"error": "Falta campo 'segundos'"}), 400
    
    try:
        segundos = int(data["segundos"])
        estado["temporizador_segundos"] = segundos
        return jsonify({"status": f"temporizador seteado a {segundos} segundos"}), 200
    except Exception:
        return jsonify({"error": "Valor inválido para segundos"}), 400

@app.route("/api/estado", methods=["GET"])
def get_estado():
    global estado
    # Retorna estado actual para que ESP32 lo consulte
    resp = {
        "servo_activado": estado["servo_activado"],
        "ultimo_activado": estado["ultimo_activado"].isoformat() if estado["ultimo_activado"] else None,
        "temporizador_segundos": estado["temporizador_segundos"]
    }
    return jsonify(resp), 200

@app.route("/api/confirmar_servo", methods=["POST"])
def confirmar_servo():
    global estado
    # ESP32 confirma que accionó el servo, se resetea estado
    estado["servo_activado"] = False
    estado["ultimo_activado"] = datetime.now()
    return jsonify({"status": "confirmación recibida"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
