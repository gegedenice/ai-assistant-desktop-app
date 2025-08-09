import os

class FileSearchTool:
    def __init__(self, root_dir="."):
        self.root_dir = root_dir

    def search(self, query: str):
        matches = []
        for dirpath, _, files in os.walk(self.root_dir):
            for filename in files:
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            matches.append(filepath)
                except Exception:
                    pass
        return matches