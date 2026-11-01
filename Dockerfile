FROM python:3.10-slim

# Instalar dependencias del sistema para Kivy, Xvfb, VNC y noVNC
RUN apt-get update && apt-get install -y \
    libsdl2-dev libsdl2-ttf-dev libsdl2-image-dev libsdl2-mixer-dev \
    libgstreamer1.0-dev gstreamer1.0-alsa gstreamer1.0-plugins-base \
    libsmpeg-dev libswscale-dev libavformat-dev libavcodec-dev \
    libjpeg-dev libtiff5-dev libx11-dev libmtdev-dev \
    build-essential libgl1-mesa-dev libgles2-mesa-dev \
    xvfb x11vnc novnc websockify \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar archivos del proyecto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Dar permisos al script de entrada
RUN chmod +x entrypoint.sh

# Render inyecta la variable $PORT, pero exponemos la interna por si acaso
EXPOSE 5900

CMD ["./entrypoint.sh"]
