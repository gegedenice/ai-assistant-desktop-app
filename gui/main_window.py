import tkinter as tk
from tkinter import ttk
import importlib.util
import subprocess
import threading
from assistant_core.assistant import Assistant
from assistant_core.providers import OpenAIProvider, GroqProvider, LocalTransformersProvider
from .dialogs import MCPManagerDialog, ApiKeysDialog
from config.settings import settings
from assistant_core.process_manager import process_manager

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Assistant")
        self.geometry("600x450")

        self._create_menu()
        self._create_widgets()

        # Assistant will be initialized on the first `on_send` call
        self.assistant = None

        self.provider_var = tk.StringVar(self)
        self.provider_var.set(settings.get_selected_provider())
        self.model_var = tk.StringVar(self)
        self.model_var.set(settings.get_selected_model())

        self._update_models_list()

    def _create_menu(self):
        self.menu_bar = tk.Menu(self)

        # File Menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Manage API Keys", command=self.open_api_keys_manager)
        file_menu.add_command(label="Manage MCP Servers", command=self.open_mcp_manager)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Provider Menu
        provider_menu = tk.Menu(self.menu_bar, tearoff=0)
        provider_menu.add_radiobutton(label="OpenAI", variable=self.provider_var, value="openai", command=self._on_provider_changed)
        provider_menu.add_radiobutton(label="Groq", variable=self.provider_var, value="groq", command=self._on_provider_changed)
        provider_menu.add_radiobutton(label="Local Transformers", variable=self.provider_var, value="local_transformers", command=self._on_provider_changed)
        self.menu_bar.add_cascade(label="Provider", menu=provider_menu)

        self.config(menu=self.menu_bar)

    def _update_models_list(self):
        provider_name = self.provider_var.get()

        if provider_name == "openai":
            models = OpenAIProvider.get_models()
        elif provider_name == "groq":
            models = GroqProvider.get_models()
        elif provider_name == "local_transformers":
            models = LocalTransformersProvider.get_models()
        else:
            models = []

        self.model_menu['values'] = models
        if models:
            current_model = self.model_var.get()
            if current_model not in models:
                self.model_var.set(models[0])
                settings.set_selected_model(models[0])
        else:
            self.model_var.set("")

    def _on_provider_changed(self):
        provider = self.provider_var.get()
        settings.set_selected_provider(provider)
        self._update_models_list()
        print(f"Switched to {provider} provider.")

        if provider == "local_transformers":
            threading.Thread(target=self._setup_local_transformers, daemon=True).start()

    def _setup_local_transformers(self):
        if importlib.util.find_spec("transformers") is None:
            print("transformers library not found. Installing...")
            self.output_text.insert(tk.END, "> Assistant: Installing transformers library. This may take a moment...\n")
            self.output_text.update_idletasks()

            try:
                subprocess.check_call(["uv", "pip", "install", "git+https://github.com/huggingface/transformers.git"])
                self.output_text.insert(tk.END, "> Assistant: transformers library installed successfully.\n")
            except subprocess.CalledProcessError as e:
                self.output_text.insert(tk.END, f"> Assistant: Error installing transformers: {e}\n")
                return

        print("Starting local transformers server...")
        self.output_text.insert(tk.END, "> Assistant: Starting local transformers server...\n")
        process_manager.start_process("uv", ["run", "python", "-m", "transformers.commands.serve", "local", "--port", "8008"], name="Transformers Server")

    def _on_model_changed(self, event=None):
        model = self.model_var.get()
        settings.set_selected_model(model)
        print(f"Switched to model {model}")

    def _create_widgets(self):
        # Top frame for provider and model selection
        top_frame = tk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(top_frame, text="Model:").pack(side="left")
        self.model_menu = ttk.Combobox(top_frame, textvariable=self.model_var)
        self.model_menu.pack(side="left", padx=5)
        self.model_menu.bind("<<ComboboxSelected>>", self._on_model_changed)

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

