import json
import os

def load_documents(name):
    path = os.path.join("data", f"{name}.json")
    if not os.path.exists(path):
        return {}
    
    with open(path, "r") as f:
        return json.load(f)

def save_documents(name, documents):
    path = os.path.join("data", f"{name}.json")
    temp_path = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(temp_path, "w") as f:
        json.dump(documents, f, indent=4)
    os.replace(temp_path, path)