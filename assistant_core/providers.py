import openai
import os
import json
import time

class BaseProvider:
    def handle_chat(self, user_input: str, tools: list, tool_invoker: callable) -> str:
        raise NotImplementedError()

    def handle_chat_stream(self, user_input: str, tools: list, tool_invoker: callable, stream_callback: callable):
        """Streaming version of handle_chat. Override in subclasses for streaming support."""
        # Default implementation: call non-streaming version and stream the result
        response = self.handle_chat(user_input, tools, tool_invoker)
        for char in response:
            stream_callback(char)
            import time
            time.sleep(0.01)  # Small delay to simulate streaming

    @classmethod
    def get_models(cls):
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
            self.client = openai.OpenAI(base_url="https://api.openai.com/v1",api_key=self.api_key)

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

    def handle_chat_stream(self, user_input: str, tools: list, tool_invoker: callable, stream_callback: callable):
        """Streaming version of handle_chat for OpenAI."""
        if not self.api_key:
            error_msg = "Error: OpenAI API key is not configured. Please set it via the File -> Manage API Keys menu."
            stream_callback(error_msg)
            return error_msg

        # Initialize client now that we know we have a key and need to use it
        if self.client is None:
            self.client = openai.OpenAI(base_url="https://api.openai.com/v1", api_key=self.api_key)

        self.messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=tools,
                tool_choice="auto",
                stream=True,
            )
            
            response_content = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    response_content += token
                    stream_callback(token)
            
            # Handle tool calls if any
            if hasattr(chunk.choices[0].delta, 'tool_calls') and chunk.choices[0].delta.tool_calls:
                # For simplicity, we'll handle tool calls in non-streaming mode
                # This could be enhanced to stream tool call responses
                pass
            
            self.messages.append({"role": "assistant", "content": response_content})
            return response_content
            
        except Exception as e:
            error_msg = f"Error calling OpenAI API: {e}"
            stream_callback(error_msg)
            return error_msg

    @classmethod
    def get_models(cls):
        api_key = settings.get_api_key("openai") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return []
        try:
            client = openai.OpenAI(base_url="https://api.openai.com/v1", api_key=api_key)
            models = client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            print(f"Error fetching OpenAI models: {e}")
            return []


class GroqProvider(BaseProvider):
    def __init__(self, api_key=None, model="llama3-8b-8192"):
        # Prioritize settings, then environment variable, then direct parameter
        self.api_key = settings.get_api_key("groq") or os.getenv("GROQ_API_KEY") or api_key

        # The client will be initialized on-demand to avoid errors if key is not set at startup
        self.client = None
        self.model = model
        self.messages = []

    def handle_chat(self, user_input: str, tool_schemas: list, tool_invoker: callable) -> str:
        if not self.api_key:
            return "Error: Groq API key is not configured. Please set it via the File -> Manage API Keys menu."

        # Initialize client now that we know we have a key and need to use it
        if self.client is None:
            self.client = openai.OpenAI(base_url="https://api.groq.com/openai/v1",api_key=self.api_key)

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
            return f"Error calling Groq API: {e}"

    def handle_chat_stream(self, user_input: str, tools: list, tool_invoker: callable, stream_callback: callable):
        """Streaming version of handle_chat for Groq."""
        if not self.api_key:
            error_msg = "Error: Groq API key is not configured. Please set it via the File -> Manage API Keys menu."
            stream_callback(error_msg)
            return error_msg

        # Initialize client now that we know we have a key and need to use it
        if self.client is None:
            self.client = openai.OpenAI(base_url="https://api.groq.com/openai/v1", api_key=self.api_key)

        self.messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=tools,
                tool_choice="auto",
                stream=True,
            )
            
            response_content = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    response_content += token
                    stream_callback(token)
            
            # Handle tool calls if any
            if hasattr(chunk.choices[0].delta, 'tool_calls') and chunk.choices[0].delta.tool_calls:
                # For simplicity, we'll handle tool calls in non-streaming mode
                pass
            
            self.messages.append({"role": "assistant", "content": response_content})
            return response_content
            
        except Exception as e:
            error_msg = f"Error calling Groq API: {e}"
            stream_callback(error_msg)
            return error_msg

    @classmethod
    def get_models(cls):
        api_key = settings.get_api_key("groq") or os.getenv("GROQ_API_KEY")
        if not api_key:
            return []
        try:
            client = openai.OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
            models = client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            print(f"Error fetching Groq models: {e}")
            return []


class LocalTransformersProvider(BaseProvider):
    def __init__(self, model="distilbert-base-uncased"):
        self.client = openai.OpenAI(base_url="http://localhost:8008/v1", api_key="local")
        self.model = model
        self.messages = []

    def handle_chat(self, user_input: str, tool_schemas: list, tool_invoker: callable) -> str:
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
            return f"Error calling Local Transformers API: {e}"

    def handle_chat_stream(self, user_input: str, tools: list, tool_invoker: callable, stream_callback: callable):
        """Streaming version of handle_chat for Local Transformers."""
        # Client is already initialized in __init__ for local transformers
        self.messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=tools,
                tool_choice="auto",
                stream=True,
            )
            
            response_content = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    response_content += token
                    stream_callback(token)
            
            # Handle tool calls if any
            if hasattr(chunk.choices[0].delta, 'tool_calls') and chunk.choices[0].delta.tool_calls:
                # For simplicity, we'll handle tool calls in non-streaming mode
                pass
            
            self.messages.append({"role": "assistant", "content": response_content})
            return response_content
            
        except Exception as e:
            error_msg = f"Error calling Local Transformers API: {e}"
            stream_callback(error_msg)
            return error_msg

    @classmethod
    def get_models(cls):
        try:
            client = openai.OpenAI(base_url="http://localhost:8008/v1", api_key="local")
            models = client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            print(f"Error fetching Local Transformers models: {e}")
            # Return a default model if the server is not running
            return ["local-model"]


class RemoteTransformersProvider(BaseProvider):
    def __init__(self, model="distilbert-base-uncased", base_url: str | None = None):
        # base_url is expected to be like https://host:port/v1
        self.base_url = base_url or settings.get_remote_transformers_url()
        self.model = model
        self.messages = []
        # Initialize lazily so we can return a helpful error if URL is missing
        self.client = None

    def _ensure_client(self):
        if self.client is None:
            if not self.base_url:
                raise ValueError("Remote Transformers URL is not configured. Please set it in Settings.")
            self.client = openai.OpenAI(base_url=self.base_url, api_key="remote")

    def handle_chat(self, user_input: str, tool_schemas: list, tool_invoker: callable) -> str:
        try:
            self._ensure_client()
        except Exception as e:
            return f"Error: {e}"
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
            return f"Error calling Remote Transformers API: {e}"

    def handle_chat_stream(self, user_input: str, tools: list, tool_invoker: callable, stream_callback: callable):
        """Streaming version of handle_chat for Remote Transformers."""
        try:
            self._ensure_client()
        except Exception as e:
            error_msg = f"Error: {e}"
            stream_callback(error_msg)
            return error_msg

        self.messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=tools,
                tool_choice="auto",
                stream=True,
            )
            
            response_content = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    response_content += token
                    stream_callback(token)
            
            # Handle tool calls if any
            if hasattr(chunk.choices[0].delta, 'tool_calls') and chunk.choices[0].delta.tool_calls:
                # For simplicity, we'll handle tool calls in non-streaming mode
                pass
            
            self.messages.append({"role": "assistant", "content": response_content})
            return response_content
            
        except Exception as e:
            error_msg = f"Error calling Remote Transformers API: {e}"
            stream_callback(error_msg)
            return error_msg

    @classmethod
    def get_models(cls):
        base_url = settings.get_remote_transformers_url()
        if not base_url:
            return []
        try:
            client = openai.OpenAI(base_url=base_url, api_key="remote")
            models = client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            print(f"Error fetching Remote Transformers models: {e}")
            return []