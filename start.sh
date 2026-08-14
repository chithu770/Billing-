#!/bin/bash
set -e

# Setup the display port
export DISPLAY=:0

# Start X virtual framebuffer
echo "Starting Xvfb..."
Xvfb :0 -screen 0 1920x1080x24 -nolisten tcp &
sleep 2

# Start Fluxbox window manager
echo "Starting fluxbox..."
fluxbox &
sleep 1

# Start x11vnc without password
echo "Starting x11vnc..."
x11vnc -display :0 -nopw -listen localhost -xkb -forever -bg

# Run the python app in the background
echo "Starting main.py..."
python main.py &

# Start noVNC to serve the VNC stream over HTTP
# Render dynamically assigns the port via the $PORT environment variable.
PORT=${PORT:-10000}
echo "Starting noVNC on port $PORT..."
websockify --web /usr/share/novnc/ $PORT localhost:5900
