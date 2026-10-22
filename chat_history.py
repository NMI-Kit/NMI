import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "chat_history.json"
ANSWER_KEY_FILE = BASE_DIR / "answer_key.json"


def load_history():

    if not HISTORY_FILE.exists():
        return []

    with open(HISTORY_FILE, "r", encoding="utf-8") as file:
        history = json.load(file)

    return history


def save_history(history):

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii=False, indent=4)


def load_answer_key():
    """The hidden answer key of the open Bagrut question, or None."""

    if not ANSWER_KEY_FILE.exists():
        return None

    with open(ANSWER_KEY_FILE, "r", encoding="utf-8") as file:
        key = json.load(file)

    return key if isinstance(key, str) and key.strip() else None


def save_answer_key(key):

    with open(ANSWER_KEY_FILE, "w", encoding="utf-8") as file:
        json.dump(key, file, ensure_ascii=False)
