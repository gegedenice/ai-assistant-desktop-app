import pandas as pd
import os
import io
from contextlib import redirect_stdout

class CodeExecutorTool:
    def execute_csv_task(self, filepath: str, new_column_name: str, colA: str, colB: str):
        df = pd.read_csv(filepath)
        df[new_column_name] = df[colA].astype(str) + df[colB].astype(str)
        version = 1
        base, ext = os.path.splitext(filepath)
        new_filepath = f"{base}_v{version}{ext}"
        while os.path.exists(new_filepath):
            version += 1
            new_filepath = f"{base}_v{version}{ext}"
        df.to_csv(new_filepath, index=False)
        return new_filepath

    def execute_python(self, code: str) -> str:
        """
        Executes a string of Python code in a sandboxed environment and returns the output.
        Only 'print' statements will be captured as output.
        """
        if "__" in code or "import" in code or "eval" in code or "exec" in code or "open" in code:
            return "Error: Use of restricted keywords is not allowed for security reasons."

        f = io.StringIO()
        with redirect_stdout(f):
            try:
                exec(code, {'__builtins__': {'print': print}}, {})
            except Exception as e:
                return f"Error executing code: {e}"

        return f.getvalue()