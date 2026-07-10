from langchain_community.chat_message_histories import ChatMessageHistory

memory_store = {}


def get_memory(user):

    key = (
        str(user.id)
        if user.is_authenticated
        else "anonymous"
    )

    if key not in memory_store:
        memory_store[key] = ChatMessageHistory()

    return memory_store[key]