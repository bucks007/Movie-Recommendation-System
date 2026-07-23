from langchain_core.chat_history import InMemoryChatMessageHistory

history_store = {}
state_store = {}


def default_state():
    return {

        # Current movie context
        "last_movie_id": None,
        "last_movie": None,
        "last_director": None,
        "last_actors": None,
        "last_genres": None,

        # Recommendation context
        "last_recommendations": [],

        # Search context
        "last_search": None,

        # Active filters
        "last_filters": {
            "genre": None,
            "mood": None,
            "year": None,
            "actor": None,
            "director": None,
        },
    }


def get_session_history(session_id):
    session_id = str(session_id)

    if session_id not in history_store:
        history_store[session_id] = InMemoryChatMessageHistory()

    return history_store[session_id]


def get_state(user_id):
    user_id = str(user_id)

    if user_id not in state_store:
        state_store[user_id] = default_state()

    return state_store[user_id]


def clear_state(user_id):
    user_id = str(user_id)
    state_store[user_id] = default_state()