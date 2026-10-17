from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CURRICULUM_FILE = BASE_DIR / "curriculum.txt"


def get_curriculum(country, grade):

    with open(CURRICULUM_FILE, "r", encoding="utf-8") as file:
        all_curricula = file.read()

    country = country.strip().upper()
    grade = grade.strip()

    start_marker = f"[CURRICULUM:{country}:{grade}]"
    end_marker = "[/CURRICULUM]"

    if start_marker not in all_curricula:
        return (
            f"No curriculum has been loaded for "
            f"{country}, Grade {grade}. "
            f"Do not invent curriculum requirements."
        )

    curriculum = all_curricula.split(start_marker, 1)[1]
    curriculum = curriculum.split(end_marker, 1)[0]

    return curriculum.strip()