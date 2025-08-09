from gui.main_window import MainWindow

def main():
    # The MCP server is no longer run locally.
    # The assistant now connects to external servers.
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()