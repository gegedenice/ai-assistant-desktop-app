import atexit
from gui.main_window import MainWindow
from assistant_core.process_manager import ProcessManager

def main():
    # Initialize and start MCP server processes
    process_manager = ProcessManager()
    process_manager.start_servers()

    # Register shutdown hook to terminate servers on exit
    atexit.register(process_manager.shutdown)

    # Run the GUI
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()