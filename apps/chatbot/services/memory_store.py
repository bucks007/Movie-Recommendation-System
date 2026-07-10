from langchain_core.chat_history import InMemoryChatMessageHistory

history_store = {}
state_store = {}


def get_session_history(session_id):
    session_id = str(session_id)

    if session_id not in history_store:
        history_store[session_id] = InMemoryChatMessageHistory()

    return history_store[session_id]


def get_state(user_id):
    user_id = str(user_id)

    if user_id not in state_store:
        state_store[user_id] = {}

    return state_store[user_id]


def clear_state(user_id):
    user_id = str(user_id)

    state_store[user_id] = {}