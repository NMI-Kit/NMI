def detect_subject(message):
    message = message.lower()

    if "math" in message or "رياضيات" in message:
        return "mathematics"

    elif "physics" in message or "فيزياء" in message:
        return "physics"

    elif "chemistry" in message or "كيمياء" in message:
        return "chemistry"

    elif "english" in message or "انجليزي" in message or "إنجليزي" in message:
        return "english"

    elif "history" in message or "تاريخ" in message:
        return "history"

    else:
        return "unknown"