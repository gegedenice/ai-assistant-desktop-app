import tkinter as tk
from assistant_core.assistant import Assistant
from .dialogs import MCPManagerDialog, ApiKeysDialog
from config.settings import settings

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Assistant")
        self.geometry("600x450")

        self._create_menu()
        self._create_widgets()

        # Assistant will be initialized on the first `on_send` call
        self.assistant = None

    def _create_menu(self):
        self.menu_bar = tk.Menu(self)

        # File Menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Manage API Keys", command=self.open_api_keys_manager)
        file_menu.add_command(label="Manage MCP Servers", command=self.open_mcp_manager)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        self.config(menu=self.menu_bar)

    def _create_widgets(self):
        # Main chat widgets
        self.input_text = tk.Text(self, height=4)
        self.input_text.pack(fill="x", padx=10)

        self.output_text = tk.Text(self, height=15)
        self.output_text.pack(fill="both", expand=True, padx=10, pady=5)

        self.send_button = tk.Button(self, text="Send", command=self.on_send)
        self.send_button.pack(pady=5)

    def on_send(self):
        user_input = self.input_text.get("1.0", tk.END).strip()
        if not user_input:
            return

        # Re-initialize assistant to pick up any settings changes
        # A more sophisticated approach might be to have the assistant update itself
        self.assistant = Assistant()

        self.output_text.insert(tk.END, f"> You: {user_input}\n")
        self.output_text.update_idletasks()

        response = self.assistant.handle_command(user_input)

        self.output_text.insert(tk.END, f"> Assistant: {response}\n\n")
        self.input_text.delete("1.0", tk.END)

    def open_api_keys_manager(self):
        ApiKeysDialog(self)

    def open_mcp_manager(self):
        MCPManagerDialog(self)

