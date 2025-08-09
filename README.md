# Personal Assistant Desktop App

## Overview

This Python desktop application serves as a powerful personal assistant that leverages large language models (LLMs) to perform tasks. It features a dynamic, server-based tool system, allowing it to connect to any number of external "Multi-tool Consumer Protocol" (MCP) servers to extend its capabilities. Through natural language commands, it can orchestrate tools for file searching, web browsing, code execution, and more.

---

## Goals

- **Dynamic Tool Integration**: Connect to one or more external MCP servers to dynamically acquire new tools and capabilities.
- **Extensible LLM Backend**: Use OpenAI's APIs by default, with the ability to switch between the Chat Completions API and the Assistants API.
- **Automate Real-world Tasks**: Combine information gathering, file manipulation, and code execution to automate complex workflows.
- **User-friendly Desktop GUI**: Provide a simple and clean interface for interaction, task management, and configuration.

---

## Architecture Overview

The application is architected around a client-server model for tools. The main desktop application acts as a client that connects to one or more MCP servers, which expose tools over a REST API.

```
+--------------------------------+      +--------------------------------+
|       MCP Server 1             |      |       MCP Server N             |
| (e.g., File System Tools)      |      | (e.g., Web & Code Tools)       |
| - GET /tools (schema)          |      | - GET /tools (schema)          |
| - POST /invoke (execution)     |      | - POST /invoke (execution)     |
+--------------------------------+      +--------------------------------+
          ^                                     ^
          | (HTTP Requests)                     | (HTTP Requests)
          |                                     |
+---------+-------------------------------------+----------+
|                       Desktop GUI Layer                    |
|                (User interactions, Config)                 |
+-----------------------------+------------------------------+
                              |
                              v
+-----------------------------+------------------------------+
|                      Assistant Core API                      |
| - Manages conversation state                               |
| - Fetches tools from all registered MCP servers            |
| - Dispatches tool execution requests to the correct server |
+-----------------------------+------------------------------+
                              |
                              v
+-----------------------------+------------------------------+
|                 LLM Backend / Provider Layer                 |
| - OpenAI Provider (configurable mode)                      |
|   - "Chat" Mode (Chat Completions API)                     |
|   - "Assistant" Mode (Assistants API)                      |
+------------------------------------------------------------+
```

---

## Key Components & Features

### 1. Desktop GUI Layer
- A simple and clean interface for interacting with the assistant.
- **MCP Server Management**: A built-in dialog to define and manage external MCP servers, including controlling their lifecycle.
- **API Mode Switching**: A dropdown menu to instantly switch between OpenAI's `chat` and `assistant` API modes.

### 2. Assistant Core API
- **Generic MCP Client**: The assistant dynamically fetches tool definitions from all registered servers.
- **Stateful Conversations**: Manages the history of the conversation, including user messages, assistant responses, and tool outputs.
- **Tool Orchestration**: When the LLM requests a tool, the core identifies which server hosts that tool and sends it an invocation request.

### 3. LLM Backend / Provider Layer
- **Dual API Support**: The `OpenAIProvider` can operate in two modes:
    - **`chat`**: Uses the powerful and flexible Chat Completions API. Ideal for single-turn or simple multi-turn conversations.
    - **`assistant`**: Uses the stateful Assistants API, which is designed for more complex, long-running tasks and conversations.
- **Provider Abstraction**: Built with a base class to allow for future integration of other LLM providers.

### 4. MCP Servers (External)
- These are separate, independent web servers that expose tools over a consistent API (`/tools` and `/invoke`).
- This decoupling allows for tools to be developed, deployed, and scaled independently of the main assistant application.

---

## MCP Server Management

A key feature of this application is its ability to manage the lifecycle of MCP server processes directly. Instead of requiring you to manually start and stop tool servers in a separate terminal, you can configure them within the application, and it will handle running them in the background.

### How It Works
1.  **Define a Server**: In the `File -> Manage MCP Servers` dialog, you can define a new server by providing:
    - **Name**: A user-friendly name for the server (e.g., "Filesystem Tools").
    - **URL**: The URL where the server will be accessible (e.g., `http://localhost:8000`). The assistant uses this to connect to the server.
    - **Command**: The command used to start the server (e.g., `npx`, `python`, `uvx`).
    - **Arguments**: The arguments to pass to the command.
    - **Enabled**: A checkbox to determine if the application should start this server on launch.
2.  **Automatic Process Management**: When the application starts, the built-in `ProcessManager` finds all enabled servers in your configuration and runs their commands as background processes.
3.  **Clean Shutdown**: When you close the application, the `ProcessManager` automatically terminates all the server processes it started.

### Example: Running a Filesystem Server

If you want to give the assistant access to your local files, you can use a compatible MCP server like `@modelcontextprotocol/server-filesystem`. You can configure the application to run this server for you:

1.  Navigate to `File -> Manage MCP Servers` and click **Add**.
2.  Fill in the details in the server editor window:
    - **Name**: `My Filesystem`
    - **URL**: `http://localhost:8000` (or the default port for that server)
    - **Command**: `npx`
    - **Arguments**: `-y @modelcontextprotocol/server-filesystem /path/to/your/documents`
    - **Enabled**: Make sure the checkbox is ticked.
3.  Save the configuration.

The next time you start the application, it will automatically run this command in the background, and the assistant will be able to connect to it at the specified URL to use its filesystem tools.

---

## Current Python Project Structure

```
personal_assistant/
│
├── assistant_core/
│   ├── __init__.py
│   ├── assistant.py         # Generic MCP client and orchestrator
│   └── providers.py         # LLM provider (OpenAI with dual mode)
│
├── config/
│   ├── __init__.py
│   └── settings.py          # Manages config.json (servers, API mode)
│
├── gui/
│   ├── __init__.py
│   ├── main_window.py       # Main desktop GUI app
│   └── dialogs.py           # MCP Server management dialog
│
├── requirements.txt
├── README.md
└── main.py                  # App entry point
```

---

## Installation & Setup

This project uses `uv` for fast environment and package management.

1.  **Clone the repository**
    ```bash
    git clone <repository_url>
    cd personal_assistant
    ```

2.  **Create and activate a virtual environment**
    ```bash
    uv venv
    source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    uv pip install -r requirements.txt
    ```

4.  **Configure the Assistant**
    - Run the application. It will create a `config.json` file in the root directory to store your settings.
    - **API Key**: Use the `File -> Manage API Keys` menu to add your OpenAI API key.
    - **MCP Servers**: Use the `File -> Manage MCP Servers` menu to add the URLs of the tool servers you want to connect to.

5.  **Run the application**
    ```bash
    python main.py
    ```

---

## Future Considerations

- Enhance UI with drag-and-drop for files and multi-window support.
- Add voice recognition and synthesis.
- Create example MCP server implementations for common tools (file system, web search, etc.).
- Extend to mobile platforms.
