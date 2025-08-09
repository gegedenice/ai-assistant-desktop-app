import tkinter as tk
from tkinter import simpledialog, messagebox
from config.settings import settings

class ApiKeysDialog(simpledialog.Dialog):
    def body(self, master):
        self.title("Manage API Keys")

        tk.Label(master, text="OpenAI API Key:").grid(row=0, sticky="w")

        self.openai_key_var = tk.StringVar(master)
        self.openai_key_var.set(settings.get_api_key("openai") or "")

        self.openai_key_entry = tk.Entry(master, textvariable=self.openai_key_var, width=50)
        self.openai_key_entry.grid(row=0, column=1, padx=5, pady=5)

        return self.openai_key_entry

    def apply(self):
        new_key = self.openai_key_var.get().strip()
        if new_key:
            settings.set_api_key("openai", new_key)
            messagebox.showinfo("Success", "OpenAI API Key saved.", parent=self)

class MCPManagerDialog(simpledialog.Dialog):
    def body(self, master):
        self.title("Manage MCP Servers")

        self.listbox = tk.Listbox(master, width=50)
        self.listbox.pack(padx=10, pady=10)
        self.populate_listbox()

        btn_frame = tk.Frame(master)
        self.add_btn = tk.Button(btn_frame, text="Add", command=self.add_server)
        self.add_btn.pack(side="left", padx=5)
        self.remove_btn = tk.Button(btn_frame, text="Remove", command=self.remove_server)
        self.remove_btn.pack(side="left", padx=5)
        btn_frame.pack(pady=5)

        return self.listbox # initial focus

    def populate_listbox(self):
        self.listbox.delete(0, tk.END)
        for server in settings.get_mcp_servers():
            self.listbox.insert(tk.END, server)

    def add_server(self):
        new_url = simpledialog.askstring("Add Server", "Enter MCP Server URL:", parent=self)
        if new_url:
            settings.add_mcp_server(new_url)
            self.populate_listbox()

    def remove_server(self):
        selected_index = self.listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select a server to remove.", parent=self)
            return

        selected_url = self.listbox.get(selected_index)
        settings.remove_mcp_server(selected_url)
        self.populate_listbox()

    def apply(self):
        # Settings are saved on add/remove, so nothing to do here
        pass
