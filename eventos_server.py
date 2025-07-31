from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# MongoDB URI y base de datos
MONGO_URI = "mongodb+srv://PapuSolis:928yZeBmyysbn3CN@perfectpawlsdb.odf3ljg.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["dogfeeder3_0"]

@app.route("/evento", methods=["POST"])
def recibir_evento():
    data = request.json
    if not data or "tipo" not in data or "fecha" not in data:
        return jsonify({"error": "Datos incompletos"}), 400
    
    data["timestamp"] = datetime.now()

    tipo = data["tipo"]
    if tipo == "rfid_detectado":
        collection = db.rfid_events
    elif tipo.startswith("distancia"):
        collection = db.ultrasonico_events
    else:
        collection = db.other_events

    result = collection.insert_one(data)
    data["_id"] = str(result.inserted_id)

    return jsonify({"status": "ok", "evento": data}), 200


@app.route("/upload_image", methods=["POST"])
def upload_image():
    data = request.json
    if not data or "imagen" not in data or "fecha" not in data:
        return jsonify({"error": "Datos incompletos"}), 400

    img_b64 = data["imagen"]
    fecha = data["fecha"]
    timestamp = datetime.now()

    collection = db.image_events
    result = collection.insert_one({
        "imagen": img_b64,
        "fecha": fecha,
        "timestamp": timestamp
    })

    return jsonify({"status": "ok", "id": str(result.inserted_id)}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
