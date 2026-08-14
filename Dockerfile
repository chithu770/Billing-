FROM python:3.12-slim

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for X11, VNC, and noVNC
RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    fluxbox \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy python dependencies and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Fix Windows line endings and make the start script executable
RUN sed -i 's/\r$//' start.sh && chmod +x start.sh

# Make vnc.html the default page so it loads automatically on the main URL
RUN ln -s /usr/share/novnc/vnc.html /usr/share/novnc/index.html

# Expose the default Render port
EXPOSE 10000

# Start the application via the script
CMD ["./start.sh"]
