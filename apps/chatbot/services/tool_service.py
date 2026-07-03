from .intent_service import Intent
from apps.movies.models import Movie
from apps.recommender.services.content_based import recommend_movies
from .recommendation_service import (GENRES,get_movies_by_genre,get_top_movies,get_trending_movies,get_top_rated_movies,get_latest_movies,get_movies_by_actor,get_movies_by_director,get_movies_by_year,)
from .movie_parser import MovieParser
from .rag_service import rag_answer
import re

def execute_tool(
    intent,
    user,
    message
):

    if intent == Intent.GREETING:

        return {
            "type": "text",
            "message":
                "Hello! 👋 I'm your Movie AI Assistant. Ask me for recommendations, similar movies, or information about any movie."
        }

    elif intent == Intent.HELP:

        return {
            "type": "text",
            "message":
                "I can recommend movies, find similar movies, search movies, explain plots, and provide personalized recommendations."
        }

    elif intent == Intent.RECOMMEND:

        return recommend_movies_tool(
            message
        )

    elif intent == Intent.SIMILAR:

        return similar_movies_tool(
            message
        )

    elif intent == Intent.PERSONALIZED:

        return personalized_tool(
            user
        )

    elif intent == Intent.MOVIE_INFO:

        return movie_info_tool(
            message
        )

    elif intent == Intent.SEARCH:

        return search_tool(
            message
        )
    elif intent == Intent.GENRE:

        return genre_tool(message)

    elif intent == Intent.TRENDING:

        return trending_tool(message)
    
    elif intent == Intent.TOP_RATED:

        return top_rated_tool()

    elif intent == Intent.LATEST:

        return latest_tool(message)

    elif intent == Intent.ACTOR:

        return actor_tool(message)

    elif intent == Intent.DIRECTOR_MOVIES:

        return director_movies_tool(message)

    elif intent == Intent.YEAR:

        return year_tool(message)
    
    movie = MovieParser.find_movie(message)

    if movie:
        return movie_info_tool(message)

    answer = rag_answer(message)

    return {
        "type": "text",
        "message": answer
    }

def serialize_movies(movies):

    return [
        {
            "id": movie.id,
            "title": movie.title,
            "poster": (
                movie.poster_url
                if movie.poster_url
                and movie.poster_url != "N/A"
                else "https://placehold.co/300x450?text=No+Poster"
            ),
            "rating": movie.vote_average,
            "year": (
                movie.release_date.year
                if movie.release_date
                else ""
            ),
            "genres": movie.genres,
        }
        for movie in movies
    ]
# Place Holder tools

def recommend_movies_tool(message):

    movie = MovieParser.find_movie(message)

    if movie:

        recommendations = recommend_movies(
            movie.movie_id,
            top_n=8
        )

        if recommendations:

            return {
                "type": "movies",
                "message": f"Because you like {movie.title}",
                "movies": serialize_movies(recommendations)
            }

    message = message.lower()

    for genre in GENRES:

        if genre.lower() in message:

            movies = get_movies_by_genre(genre)

            return {
                "type": "movies",
                "message": f"Recommended {genre} movies",
                "movies": serialize_movies(movies)
            }

    movies = get_top_movies()

    return {
        "type": "movies",
        "message": "Here are some highly-rated movies.",
        "movies": serialize_movies(movies)
    }

def similar_movies_tool(message):
    movie = MovieParser.find_movie(message)
    if not movie:
        return {
            "type": "text",
            "message": "I couldn't identify the movie."
        }
    recommendations = recommend_movies(
        movie.movie_id,
        top_n=8
    )
    if not recommendations:
        return {
            "type": "text",
            "message": "No similar movies found."
        }
    return {
        "type": "movies",
        "message": f"Movies similar to {movie.title}",
        "movies": serialize_movies(recommendations)
    }

def personalized_tool(user):

    return {
        "type": "text",
        "message":
            "Personalized recommendation tool will run here."
    }


def movie_info_tool(message):

    movie = MovieParser.find_movie(message)

    if not movie:

        return {

            "type": "text",

            "message": rag_answer(message)

        }

    msg = message.lower()

    if "director" in msg or "directed" in msg:

        answer = f"{movie.title} was directed by {movie.director}."

    elif "actor" in msg or "cast" in msg:

        answer = f"The main cast includes {movie.actors}."

    elif "plot" in msg or "story" in msg:

        answer = movie.overview

    elif "runtime" in msg:

        answer = f"Runtime: {movie.runtime}"

    elif "rating" in msg or "imdb" in msg:

        answer = f"IMDb Rating: ⭐ {movie.vote_average}"

    elif "release" in msg:

        answer = (
            f"Released on {movie.release_date}"
            if movie.release_date
            else "Release date not available."
        )
    
    elif "genre" in msg:

        answer = f"Genres: {movie.genres}"

    elif "overview" in msg:

        answer = movie.overview

    elif "year" in msg:

        answer = (
            f"Released in {movie.release_date.year}"
            if movie.release_date
            else "Release year not available."
        )

    else:

        answer = (
            f"🎬 {movie.title}\n\n"
            f"{movie.overview}\n\n"
            f"⭐ {movie.vote_average}"
        )

    return {

        "type": "movie_info",

        "message": answer,

        "movie": {

            "id": movie.id,

            "title": movie.title,

            "poster": (
                movie.poster_url
                if movie.poster_url and movie.poster_url != "N/A"
                else "https://placehold.co/300x450?text=No+Poster"
            ),

            "rating": movie.vote_average,

            "year": (
                movie.release_date.year
                if movie.release_date
                else ""
            )

        }

    }

def genre_tool(message):

    message = message.lower()

    genre = None

    for g in GENRES:

        if g.lower() in message:

            genre = g

            break

    if not genre:

        return {

            "type": "text",

            "message": "Which genre are you interested in?"

        }

    movies = get_movies_by_genre(genre)

    if not movies:

        return {

            "type": "text",

            "message": f"No {genre} movies found."

        }

    return {

        "type": "movies",

        "message": f"Top {genre} movies",

        "movies": serialize_movies(movies)

    }

def trending_tool(message=None):

    movies = get_trending_movies()

    return {

        "type": "movies",

        "message": "Trending Movies",

        "movies": serialize_movies(movies)

    }

def search_tool(message):

    # Remove command words from the query
    query = re.sub(
        r"\b(find|search|show)\b",
        "",
        message,
        flags=re.IGNORECASE
    ).strip()

    if not query:

        return {
            "type": "text",
            "message": "Please tell me which movie you want to search."
        }

    movie = MovieParser.find_movie(query)

    if movie:

        return {
            "type": "movies",
            "message": "I found this movie.",
            "movies": serialize_movies([movie])
        }

    movies = Movie.objects.filter(
        title__icontains=query
    ).order_by("-vote_average")[:8]

    if not movies.exists():

        return {
            "type": "text",
            "message": f"No movies found for '{query}'."
        }

    return {
        "type": "movies",
        "message": f"I found {movies.count()} movie(s).",
        "movies": serialize_movies(movies)
    }

def top_rated_tool():

    movies = get_top_rated_movies()

    return {

        "type": "movies",

        "message": "Top Rated Movies",

        "movies": serialize_movies(movies)

    }

def latest_tool(message):

    movies = get_latest_movies()

    return {

        "type": "movies",

        "message": "Latest Movies",

        "movies": serialize_movies(movies)

    }

def actor_tool(message):

    actor = message

    actor = re.sub(
        r"(movies|movie|starring|with|actor|actors)",
        "",
        message,
        flags=re.IGNORECASE,
    ).strip()

    movies = get_movies_by_actor(actor)

    if not movies:

        return {

            "type": "text",

            "message": "No movies found."

        }

    return {

        "type": "movies",

        "message": f"Movies starring {actor}",

        "movies": serialize_movies(movies)

    }

def director_movies_tool(message):

    director = re.sub(
        r"(movies|movie|directed by|movies by|films by|director)",
        "",
        message,
        flags=re.IGNORECASE,
    ).strip()

    movies = get_movies_by_director(director)

    if not movies:

        return {

            "type": "text",

            "message": "No movies found."

        }

    return {

        "type": "movies",

        "message": f"Movies directed by {director}",

        "movies": serialize_movies(movies)

    }

def year_tool(message):

    year = re.search(
        r"(19\d{2}|20\d{2})",
        message
    )

    if not year:

        return {

            "type": "text",

            "message": "Please provide a year."

        }

    movies = get_movies_by_year(
        int(year.group())
    )

    return {

        "type": "movies",

        "message": f"Movies from {year.group()}",

        "movies": serialize_movies(movies)

    }