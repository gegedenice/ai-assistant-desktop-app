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
                    # Handle args whether they are a string or a list
                    args_raw = server.get('args')
                    if isinstance(args_raw, str):
                        args_list = shlex.split(args_raw)
                    elif isinstance(args_raw, list):
                        args_list = args_raw
                    else:
                        args_list = []

                    command = [server['command']] + args_list
                    print(f"Starting server '{server['name']}': {' '.join(command)}")
                    # Use Popen for non-blocking process creation
                    # Redirect stdout/stderr to DEVNULL to prevent pipe deadlocks
                    proc = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
