import tkinter as tk
from tkinter import ttk
import importlib.util
import subprocess
import threading
import ttkbootstrap as ttk
from assistant_core.assistant import Assistant
from assistant_core.providers import OpenAIProvider, GroqProvider, LocalTransformersProvider
from .dialogs import MCPManagerDialog, ApiKeysDialog
from config.settings import settings
from assistant_core.process_manager import process_manager

class MainWindow(ttk.Window):
    def __init__(self):
        super().__init__(themename="cosmo")
        self.title("Personal Assistant")
        self.geometry("600x450")

        # Initialize variables first
        self.provider_var = tk.StringVar(self)
        self.provider_var.set(settings.get_selected_provider())
        self.model_var = tk.StringVar(self)
        self.model_var.set(settings.get_selected_model())

        # Then create menu and widgets
        self._create_menu()
        self._create_widgets()

        # Assistant will be initialized on the first `on_send` call
        self.assistant = None

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

    def _on_model_changed(self, event=None):
        model = self.model_var.get()
        settings.set_selected_model(model)
        print(f"Switched to model {model}")

    def _create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Top frame for provider and model selection
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(top_frame, text="Model:").pack(side="left")
        self.model_menu = ttk.Combobox(top_frame, textvariable=self.model_var, width=30)
        self.model_menu.pack(side="left", padx=5)
        self.model_menu.bind("<<ComboboxSelected>>", self._on_model_changed)

        # Chat frame
        chat_frame = ttk.Frame(main_frame)
        chat_frame.pack(fill="both", expand=True)

        self.output_text = tk.Text(chat_frame, height=15, wrap="word")
        self.output_text.pack(fill="both", expand=True)

        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill="x", pady=(10, 0))

        self.input_text = tk.Text(input_frame, height=4, wrap="word")
        self.input_text.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.send_button = ttk.Button(input_frame, text="Send", command=self.on_send, style="primary.TButton")
        self.send_button.pack(side="right")

        # Configure text tags for chat display
        self.output_text.tag_configure("user", foreground="black")
        self.output_text.tag_configure("assistant", foreground="blue")
        self.output_text.tag_configure("error", foreground="red")

    def on_send(self):
        user_input = self.input_text.get("1.0", tk.END).strip()
        if not user_input:
            return

        # Re-initialize assistant to pick up any settings changes
        # A more sophisticated approach might be to have the assistant update itself
        self.assistant = Assistant()

        self.output_text.insert(tk.END, f"> You: {user_input}\n", "user")
        self.output_text.update_idletasks()

        response = self.assistant.handle_command(user_input)

        if response.startswith("Error:"):
            self.output_text.insert(tk.END, f"> Assistant: {response}\n\n", "error")
        else:
            self.output_text.insert(tk.END, f"> Assistant: {response}\n\n", "assistant")

        self.input_text.delete("1.0", tk.END)

    def open_api_keys_manager(self):
        ApiKeysDialog(self)

    def open_mcp_manager(self):
        MCPManagerDialog(self)

