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

        # Initialize assistant after UI is setup, as it might depend on settings
        self.assistant = Assistant()

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
        # API Mode Switcher
        api_frame = tk.Frame(self)
        tk.Label(api_frame, text="API Mode:").pack(side="left", padx=(10, 5))
        self.api_mode_var = tk.StringVar(value=settings.get_api_mode())
        self.api_mode_menu = tk.OptionMenu(api_frame, self.api_mode_var, "chat", "assistant", command=self.on_api_mode_change)
        self.api_mode_menu.pack(side="left")
        api_frame.pack(fill="x", pady=5)

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

    def on_api_mode_change(self, mode):
        settings.set_api_mode(mode)
        # We can also show a little message or just let it apply on next send
        self.output_text.insert(tk.END, f"[System] API Mode set to '{mode}'. Changes will apply on next command.\n")