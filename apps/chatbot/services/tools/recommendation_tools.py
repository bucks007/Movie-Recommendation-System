from langchain_core.tools import tool

from ..recommendation_service import (
    get_movies_by_genre,
    get_top_movies,
)

from ..movie_serializer import serialize_movies


@tool
def recommend_by_genre(genre: str):
    """
    Recommend movies from a genre.
    """

    movies = get_movies_by_genre(genre)

    return {
        "message": f"Recommended {genre} movies.",
        "movies": serialize_movies(movies),
    }


@tool
def top_movies():
    """
    Return top rated movies.
    """

    movies = get_top_movies()

    return {
        "message": "Top movies",
        "movies": serialize_movies(movies),
    }