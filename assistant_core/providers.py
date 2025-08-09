import openai
import os
import json
import time

class BaseProvider:
    def handle_chat(self, user_input: str, tools: list, tool_invoker: callable) -> str:
        raise NotImplementedError()

from config.settings import settings

class OpenAIProvider(BaseProvider):
    def __init__(self, api_key=None, model="gpt-5"):
        # Prioritize settings, then environment variable, then direct parameter
        self.api_key = settings.get_api_key("openai") or os.getenv("OPENAI_API_KEY") or api_key

        # The client will be initialized on-demand to avoid errors if key is not set at startup
        self.client = None
        self.model = model
        self.messages = []

    def handle_chat(self, user_input: str, tool_schemas: list, tool_invoker: callable) -> str:
        if not self.api_key:
            return "Error: OpenAI API key is not configured. Please set it via the File -> Manage API Keys menu."

        # Initialize client now that we know we have a key and need to use it
        if self.client is None:
            self.client = openai.OpenAI(api_key=self.api_key)

        return self._handle_chat_completions(user_input, tool_schemas, tool_invoker)

    def _handle_chat_completions(self, user_input: str, tool_schemas: list, tool_invoker: callable) -> str:
        self.messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=tool_schemas,
                tool_choice="auto",
            )
            response_message = response.choices[0].message
            self.messages.append(response_message)

            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    tool_output = tool_invoker(function_name, function_args)

                    self.messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(tool_output),
                    })

                second_response = self.client.chat.completions.create(model=self.model, messages=self.messages)
                second_response_message = second_response.choices[0].message
                self.messages.append(second_response_message)
                return second_response_message.content

            return response_message.content
        except Exception as e:
            return f"Error calling OpenAI API: {e}"

