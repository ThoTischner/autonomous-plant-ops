#!/usr/bin/env bash
set -euo pipefail

echo "========================================="
echo "  NVIDIA Container Toolkit — Setup"
echo "  (Rancher Desktop Edition)"
echo "========================================="
echo ""

# Check if toolkit is already installed
if command -v nvidia-ctk &> /dev/null; then
    echo "nvidia-container-toolkit is already installed ($(nvidia-ctk --version 2>&1 | head -1))"
else
    echo "[1/3] Installing nvidia-container-toolkit..."
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
      | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
      | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
      | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null
    sudo apt-get update -qq
    sudo apt-get install -y -qq nvidia-container-toolkit
fi

# Configure Docker runtime
echo ""
echo "[2/3] Configuring Docker runtime..."
sudo nvidia-ctk runtime configure --runtime=docker

# Restart dockerd inside WSL (Rancher Desktop)
echo ""
echo "[3/3] Restarting Docker daemon..."
# Rancher Desktop runs dockerd differently, try multiple approaches
if pgrep -x dockerd > /dev/null; then
    sudo pkill dockerd
    sleep 3
    echo "Waiting for Rancher Desktop to restart dockerd..."
    for i in {1..30}; do
        if docker info > /dev/null 2>&1; then
            echo "Docker is back!"
            break
        fi
        sleep 1
    done
else
    echo "NOTE: Could not restart dockerd automatically."
    echo "Please restart Rancher Desktop manually:"
    echo "  1. Right-click Rancher Desktop tray icon"
    echo "  2. Click 'Quit'"
    echo "  3. Re-open Rancher Desktop"
fi

echo ""
echo "========================================="
echo "  Verifying GPU access..."
echo "========================================="
if docker run --rm --gpus all ubuntu:22.04 nvidia-smi 2>/dev/null; then
    echo ""
    echo "GPU access works! Run: docker compose up -d"
else
    echo ""
    echo "GPU not yet available. Please restart Rancher Desktop"
    echo "and then run: docker compose up -d"
fi
