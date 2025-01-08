# Base image with CUDA support
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# System dependencies (combined for efficiency)
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git

# Copy the bridge script into the ComfyUI directory.
COPY comfy_bridge.py /app/ComfyUI/

# Install PyTorch with CUDA support
WORKDIR /app/ComfyUI
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install ComfyUI dependencies
RUN pip3 install -r requirements.txt

# Install flask and requests for the bridge
RUN pip3 install flask requests

# Set Python environment variables
ENV PYTHONUNBUFFERED=1
ENV NVIDIA_VISIBLE_DEVICES=all

# Port for web UI
EXPOSE 8188

# Start both ComfyUI and the bridge (using a shell script)
WORKDIR /app/ComfyUI

# Set environment variables for remote GPU access
ENV CUDA_VISIBLE_DEVICES=0 # Or the appropriate device ID if you have multiple GPUs
ENV CUDA_DEVICE_ORDER=PCI_BUS_ID # Important for consistency
ENV DISPLAY=:0 # If you are using X11 forwarding (less likely with just CUDA)
#Add these lines if you are using nvidia-container-runtime
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
ENV NVIDIA_VISIBLE_DEVICES all
# Start both ComfyUI and the bridge (using a shell script)
WORKDIR /app

COPY start.sh /app/

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
