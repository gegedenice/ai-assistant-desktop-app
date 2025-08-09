from .providers import OpenAIProvider
from .tools.file_search import FileSearchTool
from .tools.web_browser import WebBrowserTool
from .tools.code_executor import CodeExecutorTool

class Assistant:
    def __init__(self, provider=None):
        self.provider = provider or OpenAIProvider()
        self.tools = {
            "file_search": FileSearchTool(),
            "web_browser": WebBrowserTool(),
            "code_executor": CodeExecutorTool(),
        }

    def handle_command(self, user_input: str) -> str:
        # Basic example: parse user_input to decide tool usage
        # TODO: implement better NLU or command routing logic
        if "find local files" in user_input.lower():
            query = user_input.lower().split("find local files mentioning")[-1].strip()
            results = self.tools["file_search"].search(query)
            return f"Found files:\n" + "\n".join(results)

        # Fallback: generate response from LLM
        response = self.provider.chat(user_input)
        return response