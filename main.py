import threading
from gui.main_window import MainWindow
from mcp_server.server import run_server

def main():
    # Run the MCP server in a background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Run the GUI in the main thread
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()