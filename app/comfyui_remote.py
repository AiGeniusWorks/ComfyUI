import requests
import json
import time

class RemoteGPUProvider:
    def __init__(self, remote_url):
        self.remote_url = remote_url.rstrip('/')
        self.client_id = str(time.time()) # Generate a unique client ID

    def initialize(self):
        try:
            response = requests.get(f"{self.remote_url}/system_stats")
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            print("Successfully connected to remote ComfyUI")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to {self.remote_url}: {e}")

    def queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        try:
            response = requests.post(f"{self.remote_url}/prompt", data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error queueing prompt: {e}")
            return None

    def get_history(self, prompt_id):
        try:
            response = requests.get(f"{self.remote_url}/history/{prompt_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting history: {e}")
            return None

    def get_images(self, ws, prompt):
        prompt_id = ws['prompt_id']
        output_images = {}
        if ws['status']['value'] == "executing":
            print(f"Executing: {ws['status']['value']}: {ws['status']['text']}")
        if ws['status']['value'] == "success":
            for node_id in ws['outputs']:
                node_output = ws['outputs'][node_id]
                if 'images' in node_output:
                    images_output = []
                    for image in node_output['images']:
                        image_data = requests.get(f"{self.remote_url}/view/{image['filename']}").content
                        images_output.append(image_data)
                    output_images[node_id] = images_output
        return output_images

class ComfyUIRemoteExecutor:
    def __init__(self, remote_url="https://comfyui-ozkwkgrp.az-csprod1.cloud-station.io"):
        self.provider = RemoteGPUProvider(remote_url)
        self.provider.initialize()

    def execute_workflow(self, workflow):
        prompt_id = self.provider.queue_prompt(workflow)
        if prompt_id is not None:
            prompt_id = prompt_id['prompt_id']
            while True:
                out = self.provider.get_history(prompt_id)
                if out is not None:
                    if out[prompt_id]['status']['value'] == "success":
                        images = self.provider.get_images(out[prompt_id], workflow)
                        return images
                    elif out[prompt_id]['status']['value'] == "executing":
                        time.sleep(1)
                    else:
                        print(f"Workflow execution failed with status: {out[prompt_id]['status']['value']}")
                        return None
                else:
                    print("Error checking workflow status.")
                    return None
        else:
            print("Error queueing prompt.")
            return None


if __name__ == "__main__":
    executor = ComfyUIRemoteExecutor()

    # Example workflow (replace with your actual workflow)
    workflow = {
        "1": {
            "inputs": {
                "text": "A cat wearing a hat",
                "clip": ["2", 0]
            },
            "class_type": "CLIPTextEncode"
        },
        "2": {
            "inputs": {
                "ckpt_path": "sd-1.5.ckpt"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "3": {
            "inputs": {
                "samples": ["4", 0]
            },
            "class_type": "VAEDecode"
        },
        "4": {
            "inputs": {
                "samples": ["1", 0],
                "noise_seed": 0,
                "steps": 20,
                "cfg": 7,
                "width": 512,
                "height": 512,
                "sampler_name": "euler_ancestral",
                "scheduler": "normal",
                "denoise": 1
            },
            "class_type": "KSampler"
        }
    }

    result = executor.execute_workflow(workflow)
    if result:
        for node_id, images in result.items():
            for i, image_data in enumerate(images):
                with open(f"output_{node_id}_{i}.png", "wb") as f:
                    f.write(image_data)
                print(f"Image saved to output_{node_id}_{i}.png")
    else:
        print("Workflow execution failed.")
