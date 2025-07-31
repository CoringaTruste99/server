from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import base64

app = Flask(__name__)
CORS(app)

# MongoDB URI
client = MongoClient("mongodb+srv://PapuSolis:928yZeBmyysbn3CN@perfectpawlsdb.odf3ljg.mongodb.net/")
db = client["dogfeeder3_0"]

@app.route("/evento", methods=["POST"])
def recibir_evento():
    try:
        data = request.get_json()
        tipo = data.get("tipo")
        fecha = data.get("fecha")
        timestamp = datetime.now()

        if tipo == "rfid_detectado":
            col = db.rfid_events
        elif tipo == "distancia_superior_20cm":
            col = db.ultrasonic_events
        else:
            return jsonify({"error": "Tipo de evento no soportado"}), 400

        evento = {
            "tipo": tipo,
            "fecha": fecha,
            "timestamp": timestamp
        }

        resultado = col.insert_one(evento)

        return jsonify({"status": "ok", "evento_id": str(resultado.inserted_id)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/upload_image", methods=["POST"])
def upload_image():
    try:
        data = request.get_json()
        img_b64 = data.get("imagen")
        fecha = data.get("fecha")
        timestamp = datetime.now()

        if not img_b64:
            return jsonify({"error": "No se recibió imagen"}), 400

        col = db.images
        evento = {
            "imagen_base64": img_b64,
            "fecha": fecha,
            "timestamp": timestamp
        }
        resultado = col.insert_one(evento)

        # Guardado local eliminado para deploy en Render

        return jsonify({"status": "ok", "imagen_id": str(resultado.inserted_id)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
