import subprocess
import shlex
from config.settings import settings

class ProcessManager:
    def __init__(self):
        self.processes = []

    def start_servers(self):
        servers = settings.get_mcp_servers()
        for server in servers:
            if server.get('enabled') and server.get('command'):
                try:
                    command = [server['command']] + shlex.split(server.get('args', ''))
                    print(f"Starting server '{server['name']}': {' '.join(command)}")
                    # Use Popen for non-blocking process creation
                    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    self.processes.append(proc)
                except Exception as e:
                    print(f"Failed to start server '{server['name']}': {e}")

    def shutdown(self):
        print("Shutting down all managed server processes...")
        for proc in self.processes:
            proc.terminate() # Send SIGTERM

        # Optional: wait for processes to terminate gracefully
        for proc in self.processes:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Process {proc.pid} did not terminate gracefully, killing.")
                proc.kill() # Send SIGKILL

        print("Shutdown complete.")
