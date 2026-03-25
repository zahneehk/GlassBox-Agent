#!/bin/bash
set -e

DISPLAY=:99
SCREEN_RESOLUTION=${SCREEN_RESOLUTION:-1280x720x24}
VNC_PORT=${VNC_PORT:-5900}
NOVNC_PORT=${NOVNC_PORT:-6080}

echo "[runner] Starting Xvfb on $DISPLAY ($SCREEN_RESOLUTION)"
Xvfb $DISPLAY -screen 0 $SCREEN_RESOLUTION -ac &
sleep 1

echo "[runner] Starting fluxbox"
DISPLAY=$DISPLAY fluxbox &
sleep 1

echo "[runner] Starting x11vnc on port $VNC_PORT"
x11vnc -display $DISPLAY -nopw -listen 0.0.0.0 -rfbport $VNC_PORT -forever -shared &
sleep 1

echo "[runner] Starting noVNC websockify on port $NOVNC_PORT"
/opt/noVNC/utils/novnc_proxy --vnc localhost:$VNC_PORT --listen $NOVNC_PORT &

echo "[runner] Starting Node.js runner"
export DISPLAY=$DISPLAY
exec node /app/dist/index.js
