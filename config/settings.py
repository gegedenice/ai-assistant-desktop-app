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
                "selected_provider": "openai",
                "selected_model": "gpt-4",
                "remote_transformers_url": "",
                "mcp_servers": [],
                "api_keys": {}
            }

        with open(self.config_file, 'r') as f:
            settings = json.load(f)
            # Ensure api_keys key exists for backward compatibility
            if "api_keys" not in settings:
                settings["api_keys"] = {}
            # Ensure remote_transformers_url exists for backward compatibility
            if "remote_transformers_url" not in settings:
                settings["remote_transformers_url"] = ""
            return settings

    def save(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()

    def get_mcp_servers(self):
        # Ensure backward compatibility for users with old config
        servers = self.get("mcp_servers", [])
        if servers and isinstance(servers[0], str):
            # Convert old string-based list to new object-based list
            new_servers = [{"name": f"Server {i+1}", "url": url, "enabled": True, "command": "", "args": ""} for i, url in enumerate(servers)]
            self.set("mcp_servers", new_servers)
            return new_servers
        return servers

    def add_mcp_server(self, server_definition):
        servers = self.get_mcp_servers()
        servers.append(server_definition)
        self.set("mcp_servers", servers)

    def update_mcp_server(self, index, server_definition):
        servers = self.get_mcp_servers()
        if 0 <= index < len(servers):
            servers[index] = server_definition
            self.set("mcp_servers", servers)

    def remove_mcp_server(self, index):
        servers = self.get_mcp_servers()
        if 0 <= index < len(servers):
            servers.pop(index)
            self.set("mcp_servers", servers)

    def get_api_key(self, provider):
        return self.get("api_keys", {}).get(provider)

    def set_api_key(self, provider, key):
        keys = self.get("api_keys", {})
        keys[provider] = key
        self.set("api_keys", keys)

    def get_selected_provider(self):
        return self.get("selected_provider", "openai")

    def set_selected_provider(self, provider):
        self.set("selected_provider", provider)

    def get_selected_model(self):
        return self.get("selected_model")

    def set_selected_model(self, model):
        self.set("selected_model", model)

    # Remote Transformers URL management
    def get_remote_transformers_url(self):
        return self.get("remote_transformers_url", "")

    def set_remote_transformers_url(self, url):
        self.set("remote_transformers_url", url)

# Global settings instance
settings = Settings()
