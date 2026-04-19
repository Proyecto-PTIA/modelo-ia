from flask import Flask, request, jsonify
import os
import json
import uuid
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from models.modelo_clip import predecir_plato

# 🔹 Config inicial
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

# 🔹 Función segura para cargar JSON
def load_json(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}

# 🔹 Ruta de prueba
@app.route("/", methods=["GET"])
def home():
    return {"mensaje": "API de IA funcionando 🚀"}

# 🔹 Endpoint IA (LIMPIO)
@app.route("/detect-dish", methods=["POST"])
def detect_dish():
    try:
        # 🔸 Validar imagen
        if "foto" not in request.files:
            return jsonify({"error": "No se envió imagen"}), 400

        foto = request.files["foto"]

        if foto.filename == "":
            return jsonify({"error": "Nombre de archivo vacío"}), 400

        # 🔸 Guardar imagen temporal
        upload_folder = os.path.join(BASE_DIR, "static", "uploads")
        os.makedirs(upload_folder, exist_ok=True)

        filename = str(uuid.uuid4()) + "_" + secure_filename(foto.filename)
        ruta = os.path.join(upload_folder, filename)
        foto.save(ruta)

        # 🔥 Predicción IA
        plato = predecir_plato(ruta).lower().strip()

        # 🔥 Eliminar imagen (importante)
        if os.path.exists(ruta):
            os.remove(ruta)

        # 🔸 Cargar SOLO lo necesario
        mapa = load_json(os.path.join(BASE_DIR, "data", "map_plato_ingredientes.json"))

        ingredientes = mapa.get(plato, [])

        # 🔥 Respuesta MINIMAL
        return jsonify({
            "plato": plato,
            "ingredientes": ingredientes
        })

    except Exception as e:
        return jsonify({
            "error": "Error interno en el servidor",
            "detalle": str(e)
        }), 500


# 🔹 Run local
if __name__ == "__main__":
    app.run(debug=True)