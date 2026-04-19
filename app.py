from flask import Flask, request, jsonify
import os
import json
import uuid
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Importación de tu modelo (asegúrate de que la ruta sea correcta en tu repo)
from models.modelo_clip import predecir_plato

# 🔹 Config inicial
load_dotenv()
# Usamos rutas absolutas basadas en la ubicación de este archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

# 🔹 Función segura para cargar JSON
def load_json(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}

# 🔹 Ruta de prueba (Útil para verificar que el Space está arriba)
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "proyecto": "S.I.R.I. API",
        "mensaje": "Servidor funcionando correctamente 🚀"
    })

# 🔹 Endpoint IA
@app.route("/detect-dish", methods=["POST"])
def detect_dish():
    try:
        # 🔸 Validar que llegue el campo 'foto'
        if "foto" not in request.files:
            return jsonify({"error": "No se envió ninguna imagen en el campo 'foto'"}), 400

        foto = request.files["foto"]

        if foto.filename == "":
            return jsonify({"error": "El archivo no tiene nombre"}), 400

        # 🔸 Carpeta temporal de subidas (ajustada para Docker)
        upload_folder = os.path.join(BASE_DIR, "static", "uploads")
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)

        # Nombre único para evitar colisiones entre usuarios
        filename = str(uuid.uuid4()) + "_" + secure_filename(foto.filename)
        ruta_temporal = os.path.join(upload_folder, filename)
        foto.save(ruta_temporal)

        # 🔥 Predicción IA
        # Asegúrate de que predecir_plato acepte la ruta del archivo
        plato_detectado = predecir_plato(ruta_temporal).lower().strip()

        # 🔥 Limpieza inmediata
        if os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)

        # 🔸 Cargar mapa de ingredientes
        # Verifica que la carpeta 'data' exista en la raíz de tu repo
        ruta_mapa = os.path.join(BASE_DIR, "data", "map_plato_ingredientes.json")
        mapa = load_json(ruta_mapa)

        ingredientes = mapa.get(plato_detectado, [])

        # 🔥 Respuesta JSON
        return jsonify({
            "success": True,
            "plato": plato_detectado,
            "ingredientes": ingredientes
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Error interno en el procesamiento",
            "detalle": str(e)
        }), 500

# 🔹 Configuración para ejecución
if __name__ == "__main__":
    # Esto solo se usa en desarrollo local
    # En Hugging Face, Gunicorn usará la variable 'app'
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port, debug=True)