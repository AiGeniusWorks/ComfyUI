# comfyui_remote.py
from server import PromptServer
from nodes import ExecutionClient
from remote_gpu import RemoteGPUProvider, ComfyUIRemoteExecutor

class RemoteExecutionClient(ExecutionClient):
    def __init__(self, server):
        super().__init__(server)
        self.provider = RemoteGPUProvider(host="your_gpu_server_ip", port=29500)
        self.remote_executor = ComfyUIRemoteExecutor(self.provider)
        self.provider.initialize()

    def execute_workflow(self, workflow):
        try:
            return self.remote_executor.execute_workflow(workflow)
        except Exception as e:
            print(f"Remote execution error: {e}")
            return {"error": str(e)}

    def cleanup(self):
        self.provider.cleanup()

# Modify main.py to use RemoteExecutionClient
def setup_remote_execution():
    server = PromptServer()
    server.execution_client = RemoteExecutionClient(server)
    return server

if __name__ == "__main__":
    server = setup_remote_execution()
    server.start()