import openai
import os
import json

class BaseProvider:
    def chat(self, prompt: str, tools: list = None, messages: list = None) -> str:
        raise NotImplementedError()

class OpenAIProvider(BaseProvider):
    def __init__(self, api_key=None, model="gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided or set in OPENAI_API_KEY environment variable.")
        openai.api_key = self.api_key
        self.model = model

    def chat(self, prompt: str = None, tools: list = None, messages: list = None) -> (str, str, list):
        """
        Sends a request to the OpenAI Chat Completions API.

        Args:
            prompt (str): The user's prompt.
            tools (list): A list of tool schemas available for the model to use.
            messages (list): A list of previous messages in the conversation.

        Returns:
            A tuple containing:
            - response_message (str): The content of the assistant's response.
            - tool_calls (list): A list of tool calls requested by the model, if any.
        """
        if messages is None:
            messages = [{"role": "user", "content": prompt}]

        try:
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            return response_message, tool_calls

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return f"Sorry, I encountered an error while connecting to the AI provider: {e}", None