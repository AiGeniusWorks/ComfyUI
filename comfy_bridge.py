from flask import Flask, request, jsonify
import requests
import argparse
import os

app = Flask(__name__)

class ComfyUIBridge:
    def __init__(self, remote_url):
        self.remote_url = remote_url.rstrip('/')

    def forward_workflow(self, workflow_data):
        try:
            response = requests.post(
                f"{self.remote_url}/queue",
                json=workflow_data,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

@app.route('/execute', methods=['POST'])
def execute_workflow():
    try:
        workflow_data = request.get_json()  # Use get_json() for better error handling
        result = bridge.forward_workflow(workflow_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "running"})

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8189) # Changed default port to avoid conflict
    parser.add_argument("--remote-url", default=os.environ.get("REMOTE_URL", "https://comfyui-ozkwkgrp.az-csprod1.cloud-station.io")) # Use environment variable or default
    args = parser.parse_args()

    print(f"Starting bridge server on {args.host}:{args.port}")
    print(f"Forwarding to remote ComfyUI at {args.remote_url}")

    bridge = ComfyUIBridge(args.remote_url)
    app.run(host=args.host, port=args.port, debug=False) #debug=False for production