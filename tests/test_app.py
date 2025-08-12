import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from assistant_core.assistant import Assistant
from config.settings import settings
from assistant_core.process_manager import process_manager

class TestAssistant(unittest.TestCase):

    def setUp(self):
        # Reset settings to default before each test
        settings.settings = settings._load_settings()
        # Clear any running processes
        process_manager.shutdown()

    @patch('assistant_core.providers.OpenAIProvider.handle_chat')
    def test_openai_provider(self, mock_handle_chat):
        settings.set_selected_provider("openai")
        settings.set_selected_model("gpt-4")
        assistant = Assistant()
        assistant.handle_command("test input")
        self.assertEqual(assistant.provider.__class__.__name__, "OpenAIProvider")
        self.assertEqual(assistant.provider.model, "gpt-4")
        mock_handle_chat.assert_called_once_with("test input", assistant.tool_schemas, assistant._invoke_tool)

    @patch('assistant_core.providers.GroqProvider.handle_chat')
    def test_groq_provider(self, mock_handle_chat):
        settings.set_selected_provider("groq")
        settings.set_selected_model("llama3-8b-8192")
        assistant = Assistant()
        assistant.handle_command("test input")
        self.assertEqual(assistant.provider.__class__.__name__, "GroqProvider")
        self.assertEqual(assistant.provider.model, "llama3-8b-8192")
        mock_handle_chat.assert_called_once_with("test input", assistant.tool_schemas, assistant._invoke_tool)

    @patch('assistant_core.process_manager.ProcessManager.start_process')
    @patch('assistant_core.providers.LocalTransformersProvider.handle_chat')
    def test_local_transformers_provider(self, mock_handle_chat, mock_start_process):
        settings.set_selected_provider("local_transformers")
        settings.set_selected_model("local-model")

        # This is a bit tricky to test without a real GUI.
        # The setup is triggered by the GUI's _on_provider_changed method.
        # We will simulate this by calling the setup method directly.
        # To do that, we would need to instantiate the MainWindow, which we can't.
        # So, we will test the assistant's behavior when the provider is selected.

        assistant = Assistant()
        assistant.handle_command("test input")

        self.assertEqual(assistant.provider.__class__.__name__, "LocalTransformersProvider")
        self.assertEqual(assistant.provider.model, "local-model")
        mock_handle_chat.assert_called_once_with("test input", assistant.tool_schemas, assistant._invoke_tool)

    def tearDown(self):
        # Clean up any processes that might have been started
        process_manager.shutdown()

if __name__ == '__main__':
    unittest.main()
