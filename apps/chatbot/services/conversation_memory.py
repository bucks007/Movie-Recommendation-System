from .memory_store import get_state


def remember_movie(user, movie):
    state = get_state(user.id)

    state["last_movie_id"] = movie.id
    state["last_movie"] = movie.title
    state["last_director"] = movie.director
    state["last_actors"] = movie.actors
    state["last_genres"] = movie.genres


def remember_recommendations(user, movies):
    state = get_state(user.id)
    state["last_recommendations"] = [
        movie.id for movie in movies
    ]


def remember_filters(
    user,
    genre=None,
    mood=None,
    year=None,
    director=None,
    actor=None,
):

    state = get_state(user.id)
    filters = state["last_filters"]

    if genre is not None:
        filters["genre"] = genre

    if mood is not None:
        filters["mood"] = mood

    if year is not None:
        filters["year"] = year

    if director is not None:
        filters["director"] = director

    if actor is not None:
        filters["actor"] = actor