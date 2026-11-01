#!/bin/bash
set -e

# 1. Arrancar el servidor gráfico virtual (Xvfb)
Xvfb :99 -screen 0 1280x720x24 &
export DISPLAY=:99
sleep 2

# 2. Arrancar el servidor VNC apuntando a esa pantalla virtual
x11vnc -display :99 -forever -nopw -listen 0.0.0.0 -rfbport 5900 &
sleep 2

# 3. Arrancar websockify (traduce WebSocket a VNC) y servir noVNC
# Render te dará una variable $PORT, la usamos para websockify
websockify --web /usr/share/novnc/ 0.0.0.0:$PORT localhost:5900 &

# 4. Arrancar tu aplicación Kivy
python3 gen_k_kivy_app.py