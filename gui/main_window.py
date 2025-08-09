import tkinter as tk
from assistant_core.assistant import Assistant

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Assistant")
        self.geometry("600x400")
        self.assistant = Assistant()

        self.input_text = tk.Text(self, height=4)
        self.input_text.pack(fill="x")

        self.output_text = tk.Text(self, height=15)
        self.output_text.pack(fill="both", expand=True)

        self.send_button = tk.Button(self, text="Send", command=self.on_send)
        self.send_button.pack()

    def on_send(self):
        user_input = self.input_text.get("1.0", tk.END).strip()
        if not user_input:
            return
        response = self.assistant.handle_command(user_input)
        self.output_text.insert(tk.END, f"> You: {user_input}\n")
        self.output_text.insert(tk.END, f"> Assistant: {response}\n\n")
        self.input_text.delete("1.0", tk.END)