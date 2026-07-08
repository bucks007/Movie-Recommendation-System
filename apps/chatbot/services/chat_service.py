from .chat_pipeline import chat_pipeline


def process_message(user, message):

    return chat_pipeline.invoke(
        {
            "user": user,
            "message": message,
        }
    )