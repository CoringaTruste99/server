from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient, DESCENDING
import requests

app = Flask(__name__)
CORS(app)

# --- Conexión a MongoDB ---
client = MongoClient("mongodb+srv://PapuSolis:928yZeBmyysbn3CN@perfectpawlsdb.odf3ljg.mongodb.net/")
db = client["dogfeeder3_0"]

# --------------------------------------------------------------------
# Función para enviar notificación push a todos los tokens registrados
# --------------------------------------------------------------------
def send_push_notification(title, body):
    url = "https://exp.host/--/api/v2/push/send"
    headers = {
        "Accept": "application/json",
        "Accept-encoding": "gzip, deflate",
        "Content-Type": "application/json"
    }

    tokens_doc = db.device_tokens.find_one()
    if not tokens_doc:
        return {"message": "No hay tokens registrados"}

    responses = []
    for token in tokens_doc.get("tokens", []):
        data = {
            "to": token,
            "sound": "default",
            "title": title,
            "body": body
        }
        response = requests.post(url, json=data, headers=headers)
        responses.append(response.json())
    return responses

# --------------------------------------
# Endpoint para registrar token de móvil
# --------------------------------------
@app.route("/register_token", methods=["POST"])
def register_token():
    data = request.get_json()
    token = data.get("token")
    if token:
        db.device_tokens.update_one({}, {"$addToSet": {"tokens": token}}, upsert=True)
        return jsonify({"message": "Token registrado"}), 200
    return jsonify({"error": "Token requerido"}), 400

# ---------------------------
# Endpoint de datos del Home
# ---------------------------
@app.route("/home_data", methods=["GET"])
def get_home_data():
    # Última foto
    last_image_doc = db.images.find_one(sort=[("timestamp", DESCENDING)])
    last_image = last_image_doc["imagen_base64"] if last_image_doc else None

    # Notificaciones recientes
    rfid_events = list(db.rfid_events.find().sort("timestamp", DESCENDING).limit(2))
    ultrasonic_events = list(db.ultrasonic_events.find().sort("timestamp", DESCENDING).limit(2))
    notifications = rfid_events + ultrasonic_events
    notifications.sort(key=lambda x: x.get("timestamp"), reverse=True)
    notifications = notifications[:2]

    formatted_notifications = [
        {"tipo": n.get("tipo"), "fecha": str(n.get("fecha") or n.get("timestamp"))}
        for n in notifications
    ]

    # Estado del dispensador
    last_ultrasonic = db.ultrasonic_events.find_one(sort=[("timestamp", DESCENDING)])
    estado_dispensador = {"mensaje": "Sin datos"}
    if last_ultrasonic:
        estado_dispensador = {
            "tipo": last_ultrasonic.get("tipo"),
            "fecha": str(last_ultrasonic.get("fecha") or last_ultrasonic.get("timestamp"))
        }

    return jsonify({
        "ultima_foto": last_image,
        "notificaciones": formatted_notifications,
        "estado_dispensador": estado_dispensador
    })

# ------------------------
# Endpoint: Nueva imagen
# ------------------------
@app.route("/new_image", methods=["POST"])
def new_image():
    data = request.get_json()
    imagen = data.get("imagen_base64")
    fecha = data.get("fecha")
    if imagen:
        db.images.insert_one({"imagen_base64": imagen, "fecha": fecha})
        send_push_notification("Nueva foto", "El dispensador tomó una nueva foto")
        return jsonify({"message": "Imagen guardada y notificación enviada"}), 200
    return jsonify({"error": "Imagen requerida"}), 400

# ------------------------
# Endpoint: Nuevo evento RFID
# ------------------------
@app.route("/new_rfid_event", methods=["POST"])
def new_rfid_event():
    data = request.get_json()
    tipo = data.get("tipo")
    fecha = data.get("fecha")
    if tipo:
        db.rfid_events.insert_one({"tipo": tipo, "fecha": fecha})
        send_push_notification("RFID detectado", f"Se detectó una tarjeta: {tipo}")
        return jsonify({"message": "Evento RFID guardado y notificación enviada"}), 200
    return jsonify({"error": "Tipo de evento requerido"}), 400

# ------------------------
# Endpoint: Nuevo evento ultrasónico
# ------------------------
@app.route("/new_ultrasonic_event", methods=["POST"])
def new_ultrasonic_event():
    data = request.get_json()
    tipo = data.get("tipo")
    fecha = data.get("fecha")
    if tipo:
        db.ultrasonic_events.insert_one({"tipo": tipo, "fecha": fecha})
        if "baja" in tipo.lower() or "poca" in tipo.lower() or "distancia" in tipo.lower():
            send_push_notification("Alerta de comida", "El dispensador tiene poca comida")
        return jsonify({"message": "Evento ultrasónico guardado y notificación enviada"}), 200
    return jsonify({"error": "Tipo de evento requerido"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
