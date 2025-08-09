import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
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

class ServerEditorDialog(simpledialog.Dialog):
    def __init__(self, parent, title, server=None):
        self.server = server or {}
        super().__init__(parent, title)

    def body(self, master):
        self.title(self.title)

        tk.Label(master, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.name_var = tk.StringVar(master, value=self.server.get("name", ""))
        self.name_entry = tk.Entry(master, textvariable=self.name_var, width=40)
        self.name_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(master, text="URL:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.url_var = tk.StringVar(master, value=self.server.get("url", ""))
        self.url_entry = tk.Entry(master, textvariable=self.url_var, width=40)
        self.url_entry.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(master, text="Command:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.command_var = tk.StringVar(master, value=self.server.get("command", ""))
        self.command_entry = tk.Entry(master, textvariable=self.command_var, width=40)
        self.command_entry.grid(row=2, column=1, padx=5, pady=2)

        tk.Label(master, text="Arguments:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.args_var = tk.StringVar(master, value=self.server.get("args", ""))
        self.args_entry = tk.Entry(master, textvariable=self.args_var, width=40)
        self.args_entry.grid(row=3, column=1, padx=5, pady=2)

        self.enabled_var = tk.BooleanVar(master, value=self.server.get("enabled", True))
        self.enabled_check = tk.Checkbutton(master, text="Enabled", variable=self.enabled_var)
        self.enabled_check.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        return self.name_entry

    def apply(self):
        self.result = {
            "name": self.name_var.get(),
            "url": self.url_var.get(),
            "command": self.command_var.get(),
            "args": self.args_var.get(),
            "enabled": self.enabled_var.get()
        }

class MCPManagerDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Manage MCP Servers")
        self.transient(parent)
        self.grab_set()

        self.tree = ttk.Treeview(self, columns=("Name", "URL", "Enabled"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("URL", text="URL")
        self.tree.heading("Enabled", text="Enabled")
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        self.populate_tree()

        btn_frame = tk.Frame(self)
        tk.Button(btn_frame, text="Add", command=self.add_server).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Edit", command=self.edit_server).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Remove", command=self.remove_server).pack(side="left", padx=5)
        btn_frame.pack(pady=5)

        self.wait_window(self)

    def populate_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for i, server in enumerate(settings.get_mcp_servers()):
            self.tree.insert("", "end", iid=i, values=(server["name"], server["url"], server["enabled"]))

    def add_server(self):
        editor = ServerEditorDialog(self, "Add MCP Server")
        if editor.result:
            settings.add_mcp_server(editor.result)
            self.populate_tree()

    def edit_server(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a server to edit.", parent=self)
            return

        index = int(selected_item)
        server_data = settings.get_mcp_servers()[index]

        editor = ServerEditorDialog(self, "Edit MCP Server", server=server_data)
        if editor.result:
            settings.update_mcp_server(index, editor.result)
            self.populate_tree()

    def remove_server(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a server to remove.", parent=self)
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to remove the selected server?", parent=self):
            index = int(selected_item)
            settings.remove_mcp_server(index)
            self.populate_tree()
