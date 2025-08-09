# Personal Assistant Desktop App

## Overview

This Python desktop application serves as a powerful personal assistant interfacing with your local files and folders, leveraging OpenAI's client APIs (default GPT-5) with extensibility for other providers and models (including local models like Ollama). It is designed to enable intelligent file searching, web browsing, code execution, and complex task automation through natural language commands.

---

## Goals

- **Seamless interaction** with local filesystem via natural language queries (e.g., searching files mentioning specific keywords).
- **Extensible LLM backend**: Use OpenAI GPT-5 by default, but allow configurable integration with other LLM providers/models, including local ones like Ollama.
- **Multi-tool support**: Integrate file search, web browsing, and code execution tools for a versatile assistant.
- **Automate real-world tasks** such as:
  - Searching local files
  - Gathering information from the web
  - Generating and editing code or documentation
  - Processing and modifying files (e.g., CSV)
- **User-friendly desktop GUI** for interaction and task management.

---

## Architecture Overview

```
+---------------------+
|   Desktop GUI Layer  |
| (User interactions)  |
+----------+----------+
           |
           v
+---------------------+
|  Assistant Core API  |
| - Chat + Response    |
| - Tool orchestration |
+----------+----------+
           |
           v
+-----------------------------+
|       Tool Modules           |
|                              |
| - File Search Tool           | <--> Local filesystem
| - Web Browser Tool           | <--> Web access via scraping or browser automation
| - Code Tool                  | <--> Local code execution environment
+-----------------------------+
           |
           v
+-------------------------------------+
|   LLM Backend / Provider Layer       |
| - OpenAI GPT-5 (default)             |
| - Configurable: other OpenAI models  |
| - External providers (e.g., Ollama)  |
| - MCP Server (optional for generic)  |
+-------------------------------------+
```

---

## Key Components & Features

### 1. Desktop GUI Layer

- Simple and clean interface for:
  - Inputting natural language commands
  - Viewing assistant responses and tool outputs
  - Managing ongoing tasks or saved files

### 2. Assistant Core API

- Central orchestration of conversations and tool invocation
- Parsing user intents and routing commands to appropriate tools
- Managing multi-step tasks and tool chaining

### 3. Tool Modules

- **File Search Tool**
  - Search local files by content or metadata (e.g., files mentioning "circular economy")
  - Indexing or scanning on-demand
  - Return file paths and snippets to assistant core
  - *Note:* The OpenAI Response API’s `file_search` tool is primarily designed for GPT models on OpenAI’s platform. For generic use or other providers/models, implement a custom file search module locally or use an MCP server if needed.

- **Web Browser Tool**
  - Fetch web information by scraping or headless browsing
  - Support simple queries like “search information about DocuTeam software”

- **Code Tool**
  - Execute Python code locally
  - Read and modify files (e.g., CSV manipulation with pandas)
  - Save results with version control (auto-increment version numbers)

### 4. LLM Backend / Provider Layer

- Default connection to OpenAI GPT-5 chat and response APIs
- Configurable to connect other providers/models via standardized interface
- Support integration with local models (e.g., Ollama) via local API or MCP server

---

## User Stories

- **File Search**  
  *As a user,* I want to ask the assistant:  
  > "Find local files mentioning `circular economy`"  
  *So that* I can quickly locate relevant documents without manually searching.

- **Web Research and Documentation**  
  *As a user,* I want the assistant to:  
  > "Search information about the DocuTeam software, write a technical documentation, and save the file at this path"  
  *So that* I can get drafted docs without writing from scratch.

- **Data File Manipulation**  
  *As a user,* I want the assistant to:  
  > "Read this CSV file, add a column concatenating colA and colB, and save the new CSV file with a version number"  
  *So that* I can automate data processing tasks quickly.

- **Multi-tool Task Chaining**  
  *As a user,* I want to combine tools seamlessly in one command, such as:  
  > "Find files about X, summarize their content, then search the web for related info."  
  *So that* complex workflows are simplified.

- **Provider Flexibility**  
  *As a user,* I want to easily switch or add LLM providers/models, including local ones, to balance latency, privacy, or cost.

---

## Specifications

| Feature                 | Description                                                   | Implementation Notes                                 |
|-------------------------|---------------------------------------------------------------|-----------------------------------------------------|
| Desktop GUI             | Cross-platform, lightweight (Tkinter, PyQt, or Electron+Py)  | Prefer Python-native for ease of integration        |
| OpenAI Client           | GPT-5 chat and response API as default backend               | Support authentication and API key management       |
| Provider Abstraction    | Interface for swapping LLM providers                          | Use adapter pattern to plug in OpenAI, Ollama, etc.|
| File Search             | Search file contents and metadata                             | Custom local indexing; fallback on OS search tools  |
| Web Browser Tool        | Web scraping or headless browsing                             | Use libraries like `requests` + `BeautifulSoup` or `playwright` |
| Code Tool               | Run Python scripts and file operations                        | Secure sandbox for code execution                     |
| Task Orchestration      | Multi-tool chaining and dialogue management                   | State machine or conversation context management     |
| Configuration UI       | Manage API keys, providers, model parameters                  | Secure storage of credentials                         |
| Logging & History       | Save conversation history and file action logs                | Local encrypted storage option                        |
| Security & Privacy      | Local file access permissions, safe code execution            | User warnings, sandboxing                             |

---

## Initial Python Project Structure

```
personal_assistant/
│
├── assistant_core/
│   ├── __init__.py
│   ├── assistant.py         # Main orchestration class (chat + tool routing)
│   ├── providers.py         # LLM provider interfaces (OpenAI, Ollama, etc)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── file_search.py   # Local file search tool
│   │   ├── web_browser.py   # Web scraping / browsing tool
│   │   ├── code_executor.py # Code execution & file manipulation tool
│
├── gui/
│   ├── __init__.py
│   ├── main_window.py       # Desktop GUI app (Tkinter/PyQt placeholder)
│   ├── dialogs.py           # Dialogs, config windows, etc
│
├── config/
│   ├── __init__.py
│   ├── settings.py          # API keys, model config, user prefs
│
├── utils/
│   ├── __init__.py
│   ├── logging.py           # Logging helper
│   ├── file_utils.py        # File system helpers (versioning, path ops)
│
├── tests/
│   ├── test_assistant.py
│   ├── test_tools.py
│
├── requirements.txt
├── README.md
├── main.py                  # App entry point
```

---

## Installation & Setup

1. Clone the repo  
2. Create and activate Python virtual environment  
3. Install dependencies (OpenAI SDK, web scraping libs, GUI framework)  
4. Configure OpenAI API key and other providers in settings  
5. Run the desktop app

---

## Future Considerations

- Implement MCP server support for generic file search and provider-agnostic tool invocation  
- Enhance UI with drag-and-drop for files and multi-window support  
- Add voice recognition and synthesis  
- Extend to mobile platforms
