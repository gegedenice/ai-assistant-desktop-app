import json
import os

class Settings:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.settings = self._load_settings()

    def _load_settings(self):
        if not os.path.exists(self.config_file):
            # Default settings
            return {
                "mcp_servers": [],
                "openai_api_mode": "chat"
            }
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def save(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()

    def get_mcp_servers(self):
        return self.get("mcp_servers", [])

    def add_mcp_server(self, url):
        servers = self.get_mcp_servers()
        if url not in servers:
            servers.append(url)
            self.set("mcp_servers", servers)

    def remove_mcp_server(self, url):
        servers = self.get_mcp_servers()
        if url in servers:
            servers.remove(url)
            self.set("mcp_servers", servers)

    def get_api_mode(self):
        return self.get("openai_api_mode", "chat")

    def set_api_mode(self, mode):
        if mode not in ["chat", "assistant"]:
            raise ValueError("Invalid API mode specified.")
        self.set("openai_api_mode", mode)

# Global settings instance
settings = Settings()
