def format_history(messages):

    history = []

    for m in messages:

        role = "User" if m.type == "human" else "Assistant"

        history.append(
            f"{role}: {m.content}"
        )

    return "\n".join(history)