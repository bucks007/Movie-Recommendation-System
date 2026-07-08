from langchain_core.tools import tool
from ..movie_parser import MovieParser

@tool
def movie_information(title: str):
    """
   Get detailed information about a movie.
    """

    movie = MovieParser.find_movie(title)

    if movie is None:
        return "Movie not found."

    return f"""
        Title: {movie.title}

        Genres: {movie.genres}

        Director: {movie.director}

        Actors: {movie.actors}

        IMDb Rating: {movie.vote_average}

        Overview:
        {movie.overview}
        """