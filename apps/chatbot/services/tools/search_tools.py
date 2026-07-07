from langchain_core.tools import tool
from apps.movies.models import Movie
from ..movie_serializer import serialize_movies


@tool
def search_movie(title: str):
    """
    Search movies by title.
    """

    movies = Movie.objects.filter(
        title__icontains=title
    ).order_by("-vote_average")[:10]

    return serialize_movies(movies)