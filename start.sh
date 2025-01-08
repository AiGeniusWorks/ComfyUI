#!/bin/bash

# Start ComfyUI
cd ComfyUI
python3 main.py --listen 0.0.0.0 &
cd ..

# Start the bridge (no need to pass --remote-url here)
python3 comfy_bridge.py --host 0.0.0.0 --port 8189

wait
