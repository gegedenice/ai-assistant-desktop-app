import pandas as pd
import os

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