import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
STUDENT_FILE = BASE_DIR / "student.json"


def save_student(name, grade, country, language, units=None):

    student = {
        "name": name,
        "grade": grade,
        "country": country,
        "language": language
    }
    # Older profiles have no units; keep the key out unless it is supplied.
    if units:
        student["units"] = units

    with open(STUDENT_FILE, "w", encoding="utf-8") as file:
        json.dump(student, file, ensure_ascii=False, indent=4)


def load_student():

    if not STUDENT_FILE.exists():
        return None

    with open(STUDENT_FILE, "r", encoding="utf-8") as file:
        student = json.load(file)

    return student