import flask
from flask import request, jsonify
import json
import sys
import os

# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from assistant_core.tools.file_search import FileSearchTool
from assistant_core.tools.web_browser import WebBrowserTool
from assistant_core.tools.code_executor import CodeExecutorTool

app = flask.Flask(__name__)

tools = {
    "file_search": FileSearchTool(),
    "web_browser": WebBrowserTool(),
    "code_executor": CodeExecutorTool()
}

tool_schemas = [
    {
        "type": "function",
        "function": {
            "name": "file_search",
            "description": "Search for files on the local system that contain a specific query string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The string to search for within the files."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_browser",
            "description": "Search the web for information on a given query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_csv_task",
            "description": "Read a CSV, add a new column by concatenating two existing columns, and save it as a new versioned file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the input CSV file."},
                    "new_column_name": {"type": "string", "description": "Name for the new column."},
                    "colA": {"type": "string", "description": "Name of the first column to concatenate."},
                    "colB": {"type": "string", "description": "Name of the second column to concatenate."}
                },
                "required": ["filepath", "new_column_name", "colA", "colB"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_python",
            "description": "Executes a string of Python code in a sandboxed environment and returns the output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python code to execute."
                    }
                },
                "required": ["code"]
            }
        }
    }
]

@app.route('/tools', methods=['GET'])
def get_tools():
    return jsonify(tool_schemas)

@app.route('/invoke', methods=['POST'])
def invoke_tool():
    data = request.json
    tool_name = data.get('tool')
    kwargs = data.get('kwargs', {})

    try:
        if tool_name == "file_search":
            result = tools["file_search"].search(**kwargs)
        elif tool_name == "web_browser":
            result = tools["web_browser"].search(**kwargs)
        elif tool_name == "execute_csv_task":
            result = tools["code_executor"].execute_csv_task(**kwargs)
        elif tool_name == "execute_python":
            result = tools["code_executor"].execute_python(**kwargs)
        else:
            return jsonify({"error": f"Tool '{tool_name}' not found or not configured in server"}), 404

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_server():
    app.run(port=5001)

if __name__ == '__main__':
    run_server()
