import tkinter as tk
import ttkbootstrap as ttk
import threading
from assistant_core.assistant import Assistant
from assistant_core.providers import OpenAIProvider, GroqProvider, LocalTransformersProvider, RemoteTransformersProvider
from .dialogs import MCPManagerDialog, ApiKeysDialog, RemoteTransformersUrlDialog
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
        provider_menu.add_radiobutton(label="Remote Transformers", variable=self.provider_var, value="remote_transformers", command=self._on_provider_changed)
        provider_menu.add_separator()
        provider_menu.add_command(label="Set Remote Transformers URL...", command=self.open_remote_transformers_url_dialog)
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
        elif provider_name == "remote_transformers":
            models = RemoteTransformersProvider.get_models()
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

    def _on_model_changed(self, event=None):
        model = self.model_var.get()
        settings.set_selected_model(model)

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
        
        # Add placeholder text
        self.input_text.insert("1.0", "Type your message here...")
        self.input_text.config(foreground="gray")
        self.input_text.bind("<FocusIn>", self._on_input_focus_in)
        self.input_text.bind("<FocusOut>", self._on_input_focus_out)

        self.send_button = ttk.Button(input_frame, text="Send", command=self.on_send, style="primary.TButton")
        self.send_button.pack(side="right")

        # Configure text tags for chat display
        self.output_text.tag_configure("user", foreground="black")
        self.output_text.tag_configure("assistant", foreground="blue")
        self.output_text.tag_configure("error", foreground="red")

    def on_send(self):
        user_input = self.input_text.get("1.0", tk.END).strip()
        if not user_input or user_input == "Type your message here...":
            return

        # Re-initialize assistant to pick up any settings changes
        # A more sophisticated approach might be to have the assistant update itself
        self.assistant = Assistant()

        self.output_text.insert(tk.END, f"> You: {user_input}\n", "user")
        self.output_text.update_idletasks()
        
        # Start streaming response
        self.output_text.insert(tk.END, "> Assistant: ", "assistant")
        self.output_text.update_idletasks()
        
        def stream_callback(token):
            # Use after() to schedule UI updates on the main thread
            self.after(0, lambda: self._update_streaming_output(token))
        
        # Run streaming in a separate thread to prevent UI blocking
        def streaming_thread():
            try:
                response = self.assistant.handle_command_stream(user_input, stream_callback)
                # Add newline after streaming is complete
                self.after(0, lambda: self._finish_streaming())
            except Exception as e:
                error_msg = f"Error: {e}"
                self.after(0, lambda: self._update_streaming_output(error_msg))
                self.after(0, lambda: self._finish_streaming())
        
        threading.Thread(target=streaming_thread, daemon=True).start()

        self.input_text.delete("1.0", tk.END)

    def open_api_keys_manager(self):
        ApiKeysDialog(self)

    def open_mcp_manager(self):
        MCPManagerDialog(self)

    def open_remote_transformers_url_dialog(self):
        RemoteTransformersUrlDialog(self)
        if self.provider_var.get() == "remote_transformers":
            self._update_models_list()

    def _on_input_focus_in(self, event):
        if self.input_text.get("1.0", tk.END).strip() == "Type your message here...":
            self.input_text.delete("1.0", tk.END)
            self.input_text.config(foreground="black")

    def _on_input_focus_out(self, event):
        if not self.input_text.get("1.0", tk.END).strip():
            self.input_text.insert("1.0", "Type your message here...")
            self.input_text.config(foreground="gray")

    def _update_streaming_output(self, token):
        """Update the streaming output on the main thread."""
        self.output_text.insert(tk.END, token)
        self.output_text.see(tk.END)

    def _finish_streaming(self):
        """Finish the streaming response on the main thread."""
        self.output_text.insert(tk.END, "\n\n")

