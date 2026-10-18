from student_profile import save_student, load_student


def main():
    student = load_student()

    if student is None:
        print("Welcome to NMI")

        name = input("What is your name? ").strip().title()
        grade = input("What grade are you in? ").strip()
        country = input("What country are you studying in? ").strip().title()
        language = input("What language do you prefer? ").strip().title()
        units = input("How many units do you study (3, 4 or 5)? Leave empty if not applicable: ").strip()

        save_student(name, grade, country, language, units)

    else:
        name = student["name"]
        grade = student["grade"]
        country = student["country"]
        language = student["language"]
        units = student.get("units")

        print("Welcome back,", name)

    message = input("You: ").strip()

    # Delay AI initialization until the command-line application is used.
    from ai_test import ask_ai

    reply = ask_ai(name, grade, country, language, message, units=units)
    print("NMI:", reply)


if __name__ == "__main__":
    main()
