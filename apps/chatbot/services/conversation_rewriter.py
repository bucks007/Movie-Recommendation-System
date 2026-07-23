import re

from .memory_store import get_state


def rewrite_from_memory(user, query):

    state = get_state(user.id)

    q = query.lower()

    movie = state.get("last_movie")
    director = state.get("last_director")
    genres = state.get("last_genres")

    # ----------------------------
    # Same director
    # ----------------------------

    if director:

        if (
            "same director" in q
            or "another one" in q
            or "another movie" in q
            or "more by him" in q
            or "more from him" in q
        ):
            return f"Movies directed by {director}"

    # ----------------------------
    # Emotional like previous movie
    # ----------------------------

    if movie:

        if "emotional" in q:

            return (
                f"Show emotional movies like {movie}"
            )

        if "less action" in q:

            return (
                f"Movies like {movie} but less action"
            )

        if "more action" in q:

            return (
                f"Movies like {movie} but more action"
            )

    # ----------------------------
    # Blue aliens
    # ----------------------------

    if movie:

        if (
            "blue aliens" in q
            or "pandora" in q
        ):
            return "Tell me about Avatar"

    return query