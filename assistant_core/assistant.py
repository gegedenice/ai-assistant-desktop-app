import requests
import json
from .providers import OpenAIProvider

class Assistant:
    def __init__(self, provider=None):
        self.provider = provider or OpenAIProvider()
        self.mcp_server_url = "http://127.0.0.1:5001"
        self.tools = self._fetch_tools()
        self.messages = []

    def _fetch_tools(self):
        try:
            response = requests.get(f"{self.mcp_server_url}/tools")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Could not fetch tools from MCP server: {e}")
            return []

    def handle_command(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})

        # First API call to get model's response or tool calls
        response_message, tool_calls = self.provider.chat(messages=self.messages, tools=self.tools)

        if tool_calls:
            # Add the assistant's response with tool calls to the message history
            if isinstance(response_message, str): # Handle error case from provider
                 return response_message
            self.messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Call the MCP server to execute the tool
                try:
                    api_response = requests.post(
                        f"{self.mcp_server_url}/invoke",
                        json={"tool": function_name, "kwargs": function_args}
                    )
                    api_response.raise_for_status()
                    tool_output = api_response.json().get('result', f'Error: No result found for {function_name}')
                except requests.exceptions.RequestException as e:
                    tool_output = f"Error calling tool API: {e}"

                self.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(tool_output),
                })

            # Second API call to get the final response from the model
            final_response_message, _ = self.provider.chat(messages=self.messages, tools=self.tools)
            self.messages.append(final_response_message)
            return final_response_message.content

        # If no tool calls, just return the response
        if isinstance(response_message, str):
            return response_message

        self.messages.append(response_message)
        return response_message.content