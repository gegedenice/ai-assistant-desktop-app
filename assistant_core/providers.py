class BaseProvider:
    def chat(self, prompt: str) -> str:
        raise NotImplementedError()

class OpenAIProvider(BaseProvider):
    def __init__(self, api_key=None):
        self.api_key = api_key
        # TODO: Initialize OpenAI client here

    def chat(self, prompt: str) -> str:
        # TODO: Call OpenAI chat completion API
        return f"Simulated OpenAI response to: {prompt}"