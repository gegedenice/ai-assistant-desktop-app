import subprocess
import shlex
import atexit
from config.settings import settings

class ProcessManager:
    def __init__(self):
        self.processes = []
        atexit.register(self.shutdown)

    def start_process(self, command, args, name="Process"):
        try:
            cmd_list = [command] + args
            print(f"Starting {name}: {' '.join(cmd_list)}")
            proc = subprocess.Popen(cmd_list, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.processes.append(proc)
            return proc
        except Exception as e:
            print(f"Failed to start {name}: {e}")
            return None

    def start_servers(self):
        servers = settings.get_mcp_servers()
        for server in servers:
            if server.get('enabled') and server.get('command'):
                args_raw = server.get('args')
                if isinstance(args_raw, str):
                    args_list = shlex.split(args_raw)
                elif isinstance(args_raw, list):
                    args_list = args_raw
                else:
                    args_list = []

                self.start_process(server['command'], args_list, name=server.get('name', 'MCP Server'))

    def shutdown(self):
        print("Shutting down all managed processes...")
        for proc in self.processes:
            if proc.poll() is None:
                print(f"Terminating process {proc.pid}...")
                proc.terminate()

        for proc in self.processes:
            try:
                if proc.poll() is None:
                    proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Process {proc.pid} did not terminate gracefully, killing.")
                proc.kill()

        self.processes = []
        print("Shutdown complete.")

# Global instance
process_manager = ProcessManager()
