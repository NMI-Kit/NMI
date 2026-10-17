import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
PROGRESS_FILE = BASE_DIR / "progress.json"


def load_progress():

    if not PROGRESS_FILE.exists():
        return {}

    with open(PROGRESS_FILE, "r", encoding="utf-8") as file:
        progress = json.load(file)

    return progress


def save_progress(progress):

    with open(PROGRESS_FILE, "w", encoding="utf-8") as file:
        json.dump(progress, file, ensure_ascii=False, indent=4)


def record_attempt(subject, topic, skill, correct, hint_used, mistake_type):

    progress = load_progress()

    attempt = {
        "subject": subject,
        "topic": topic,
        "skill": skill,
        "correct": correct,
        "hint_used": hint_used,
        "mistake_type": mistake_type
    }

    if "attempts" not in progress:
        progress["attempts"] = []

    progress["attempts"].append(attempt)

    save_progress(progress)


def calculate_mastery(subject, topic, skill):

    progress = load_progress()

    if "attempts" not in progress:
        return 0

    skill_attempts = []

    for attempt in progress["attempts"]:

        if (
            attempt["subject"] == subject
            and attempt["topic"] == topic
            and attempt["skill"] == skill
        ):
            skill_attempts.append(attempt)

    if len(skill_attempts) == 0:
        return 0

    correct_answers = 0

    for attempt in skill_attempts:

        if attempt["correct"] == True:
            correct_answers += 1

    mastery = correct_answers / len(skill_attempts) * 100

    return round(mastery)
def get_recurring_mistakes(subject, topic, skill):

    progress = load_progress()

    if "attempts" not in progress:
        return {}

    mistakes = {}

    for attempt in progress["attempts"]:

        if (
            attempt["subject"] == subject
            and attempt["topic"] == topic
            and attempt["skill"] == skill
            and attempt["mistake_type"]
        ):

            mistake = attempt["mistake_type"]

            if mistake not in mistakes:
                mistakes[mistake] = 1
            else:
                mistakes[mistake] += 1

    recurring_mistakes = {}

    for mistake, count in mistakes.items():

        if count >= 2:
            recurring_mistakes[mistake] = count

    return recurring_mistakes