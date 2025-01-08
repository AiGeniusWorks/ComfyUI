#!/bin/bash

# Start ComfyUI (in the background)
python3 main.py --listen 0.0.0.0 &

# Start the bridge
python3 comfy_bridge.py --host 0.0.0.0 --port 8188 --remote-url https://comfyui-ozkwkgrp.az-csprod1.cloud-station.io

# Keep the container running (optional, but recommended)
wait