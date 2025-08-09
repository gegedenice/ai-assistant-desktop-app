import requests
import json
from .providers import OpenAIProvider
from config.settings import settings

class Assistant:
    def __init__(self, provider=None):
        self.api_mode = settings.get_api_mode()
        self.provider = provider or OpenAIProvider(mode=self.api_mode)

        self.mcp_server_urls = settings.get_mcp_servers()
        self.tools_info = self._fetch_all_tools()
        self.tool_schemas = [info['schema'] for info in self.tools_info]

        self.messages = []

    def _fetch_all_tools(self):
        all_tools = []
        for url in self.mcp_server_urls:
            try:
                response = requests.get(f"{url}/tools")
                response.raise_for_status()
                server_tools = response.json()
                for tool_schema in server_tools:
                    # Store the server URL with each tool for later invocation
                    all_tools.append({"server_url": url, "schema": tool_schema})
            except requests.exceptions.RequestException as e:
                print(f"Could not fetch tools from MCP server at {url}: {e}")
        return all_tools

    def _get_server_url_for_tool(self, tool_name):
        for tool_info in self.tools_info:
            if tool_info['schema']['function']['name'] == tool_name:
                return tool_info['server_url']
        return None

    def handle_command(self, user_input: str) -> str:
        # The new provider logic will handle the different flows
        return self.provider.handle_chat(user_input, self.tool_schemas, self._invoke_tool)

    def _invoke_tool(self, tool_name, kwargs):
        server_url = self._get_server_url_for_tool(tool_name)
        if not server_url:
            return f"Error: Could not find a server for tool '{tool_name}'"

        try:
            api_response = requests.post(
                f"{server_url}/invoke",
                json={"tool": tool_name, "kwargs": kwargs}
            )
            api_response.raise_for_status()
            return api_response.json().get('result', f'Error: No result found for {tool_name}')
        except requests.exceptions.RequestException as e:
            return f"Error calling tool API: {e}"