import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "chat_history.json"


def load_history():

    if not HISTORY_FILE.exists():
        return []

    with open(HISTORY_FILE, "r", encoding="utf-8") as file:
        history = json.load(file)

    return history


def save_history(history):

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii=False, indent=4)