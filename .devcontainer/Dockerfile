FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Install GUI-related dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxcb-keysyms1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-render-util0 \
    libxcb-randr0 \
    libxcb-shape0 \
    libxkbcommon-x11-0 \
    libfontconfig1 \
    libdbus-1-3 \
    xvfb \
    fluxbox \
    x11vnc \
    novnc \
    websockify \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install project dependencies
COPY requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
   && rm -rf /tmp/pip-tmp

# Set up a script to start VNC
RUN echo '#!/bin/bash\n\
export DISPLAY=:1\n\
Xvfb :1 -screen 0 1280x1024x24 &\n\
sleep 2\n\
fluxbox &\n\
x11vnc -display :1 -nopw -forever -shared &\n\
/usr/share/novnc/utils/launch.sh --vnc localhost:5900 --listen 6080\n\
' > /usr/local/bin/start-vnc.sh && chmod +x /usr/local/bin/start-vnc.sh

EXPOSE 6080
