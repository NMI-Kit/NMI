from pathlib import Path
import re


BASE_DIR = Path(__file__).resolve().parent
CURRICULUM_DIR = BASE_DIR / "curriculum"

ISRAEL_NAMES = {"il", "isr", "israel", "إسرائيل", "اسرائيل", "ישראל"}
GRADE_NAMES = {
    "י": "10", "יא": "11", "יב": "12",
    "العاشر": "10", "عاشر": "10",
    "الحادي عشر": "11", "حادي عشر": "11",
    "الثاني عشر": "12", "ثاني عشر": "12",
}
SUBJECT_NAMES = {
    "math": "math", "mathematics": "math", "رياضيات": "math", "الرياضيات": "math", "מתמטיקה": "math",
}

NOT_READY = ("No curriculum file is loaded for this student yet. "
             "Tell the student this subject or level is not ready in NMI yet. "
             "Do not invent curriculum requirements.")


def _grade(value):
    text = str(value).strip().replace('"', "").replace("'", "").replace("״", "")
    if text in GRADE_NAMES:
        return GRADE_NAMES[text]
    digits = re.search(r"\d+", text)
    return digits.group() if digits else ""


def _units(value):
    digits = re.search(r"[345]", str(value or ""))
    return digits.group() if digits else ""


def get_curriculum(country, grade, subject="math", units=None):
    """Return the curriculum text for one student.

    File layout: curriculum/<subject>/grade<N>/<units>units.md
    """
    if str(country).strip().casefold() not in ISRAEL_NAMES:
        return NOT_READY

    folder = CURRICULUM_DIR / SUBJECT_NAMES.get(str(subject).strip().casefold(), "") / f"grade{_grade(grade)}"
    if not folder.is_dir():
        return NOT_READY

    level = _units(units)
    if not level:
        available = sorted(path.stem.replace("units", "") for path in folder.glob("*units.md"))
        return ("The student's level (units) is unknown. Before teaching, ask the student once "
                "which level they study: " + ", ".join(available) + " units.")

    file = folder / f"{level}units.md"
    if not file.exists():
        return NOT_READY
    return file.read_text(encoding="utf-8").strip()
