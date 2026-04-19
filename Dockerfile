# Usa una imagen de Python ligera
FROM python:3.10-slim

# Evita que Python genere archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --- ESTA ES LA PARTE QUE CAMBIA ---
# Instalamos libgl1 y libglib2.0-0 que son las versiones actuales
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
# -----------------------------------

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Crear carpeta de uploads con permisos
RUN mkdir -p static/uploads && chmod 777 static/uploads

# Exponer el puerto de Hugging Face
EXPOSE 7860

# Ejecutar con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]