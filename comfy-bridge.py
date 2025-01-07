from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

class ComfyUIBridge:
    def __init__(self, remote_url="https://comfyui-ozkwkgrp.az-csprod1.cloud-station.io"):
        self.remote_url = remote_url.rstrip('/')

    def forward_workflow(self, workflow_data):
        try:
            response = requests.post(
                f"{self.remote_url}/queue",
                json=workflow_data,
                headers={'Content-Type': 'application/json'}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

bridge = ComfyUIBridge()

@app.route('/execute', methods=['POST'])
def execute_workflow():
    try:
        workflow_data = request.json
        result = bridge.forward_workflow(workflow_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "running"})

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8188)
    parser.add_argument("--remote-url", default="https://comfyui-ozkwkgrp.az-csprod1.cloud-station.io")
    
    args = parser.parse_args()
    
    print(f"Starting bridge server on {args.host}:{args.port}")
    print(f"Forwarding to remote ComfyUI at {args.remote_url}")
    
    bridge = ComfyUIBridge(args.remote_url)
    app.run(host=args.host, port=args.port)