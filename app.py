from flask import Flask, request, jsonify
import os
import json
import uuid
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from recomendador import recomendar_por_texto
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

# 🔹 Endpoint principal
@app.route("/predict", methods=["POST"])
def predict():
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

        # 🔥 Eliminar imagen (liberar espacio)
        if os.path.exists(ruta):
            os.remove(ruta)

        # 🔸 Cargar datos
        mapa = load_json(os.path.join(BASE_DIR, "data", "map_plato_ingredientes.json"))
        calorias_data = load_json(os.path.join(BASE_DIR, "data", "calorias_platos.json"))
        categorias_data = load_json(os.path.join(BASE_DIR, "data", "categorias_platos.json"))
        recetas_data = load_json(os.path.join(BASE_DIR, "data", "recetas_platos.json"))
        tiempos_data = load_json(os.path.join(BASE_DIR, "data", "tiempos_preparacion.json"))

        # 🔸 Obtener información
        ingredientes = mapa.get(plato, [])
        texto = " ".join(ingredientes)

        recomendaciones = recomendar_por_texto(texto)

        total_calorias = calorias_data.get(plato, "No disponible")

        # 🔸 Clasificación nutricional
        if isinstance(total_calorias, int):
            if total_calorias < 200:
                nivel = "bajo"
            elif total_calorias < 400:
                nivel = "medio"
            else:
                nivel = "alto"
        else:
            nivel = "no_disponible"

        categorias = categorias_data.get(plato, [])
        pasos = recetas_data.get(plato, {}).get("pasos", [])
        tiempo = tiempos_data.get(plato, "No disponible")

        # 🔥 Respuesta final
        return jsonify({
            "plato": plato,
            "ingredientes": ingredientes,
            "calorias": total_calorias,
            "nivel": nivel,
            "categorias": categorias,
            "pasos": pasos,
            "tiempo_preparacion": tiempo,
            "recomendaciones": recomendaciones
        })

    except Exception as e:
        return jsonify({
            "error": "Error interno en el servidor",
            "detalle": str(e)
        }), 500


# 🔹 Run local
if __name__ == "__main__":
    app.run(debug=True)