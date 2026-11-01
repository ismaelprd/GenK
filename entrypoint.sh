#!/bin/bash
set -e

# 0. Limpiar restos de un arranque anterior (evita "Server is already active for display 99")
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99

# 1. Servidor gráfico virtual
Xvfb :99 -screen 0 1280x720x24 &
export DISPLAY=:99
sleep 2

# 2. Servidor VNC
x11vnc -display :99 -forever -nopw -listen 0.0.0.0 -rfbport 5900 &
sleep 2

# 3. Página de entrada: que "/" abra directamente la app en vez de la lista de archivos
cat > /usr/share/novnc/index.html <<'HTML'
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=vnc.html?autoconnect=true&resize=scale&path=websockify">
</head><body></body></html>
HTML

# 4. websockify + noVNC en el puerto que da Render
websockify --web /usr/share/novnc/ 0.0.0.0:${PORT:-10000} localhost:5900 &

# 5. App Kivy
python3 gen_k_kivy_app.py
