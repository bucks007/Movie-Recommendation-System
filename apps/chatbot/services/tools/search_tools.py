from langchain_core.tools import tool
from apps.movies.models import Movie
from ..movie_serializer import serialize_movies

@tool
def search_movies(query: str):
    """
    Search movies by title.
    Returns up to 10 matching movies.
    """

    movies = (
        Movie.objects
        .filter(title__icontains=query)
        .order_by("-vote_average")[:10]
    )

    return {
        "message": f"Found {movies.count()} movies.",
        "movies": serialize_movies(movies),
    }