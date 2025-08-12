from gui.main_window import MainWindow
from assistant_core.process_manager import process_manager

def main():
    # Start Transformers server once at app launch
    process_manager.start_transformers_server(port=8008)

    # Start MCP server processes
    process_manager.start_servers()

    # Run the GUI
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()