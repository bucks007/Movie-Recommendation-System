from langchain_core.tools import tool
from ..movie_parser import MovieParser

@tool
def movie_information(title: str):
    """
    Get information about a movie.
    """

    movie = MovieParser.find_movie(title)

    if movie is None:
        return "Movie not found."

    return {
        "title": movie.title,
        "overview": movie.overview,
        "director": movie.director,
        "actors": movie.actors,
        "rating": movie.vote_average,
    }