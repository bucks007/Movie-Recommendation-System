from apps.movies.models import Movie
from apps.recommender.services.personalized import recommend_personalized
from .intent_service import Intent
from apps.recommender.services.content_based import recommend_movies
from .recommendation_service import (GENRES,get_movies_by_genre,get_top_movies,get_trending_movies,get_top_rated_movies,get_latest_movies,get_movies_by_actor,get_movies_by_director,get_movies_by_year,)
from .movie_parser import MovieParser
from .context_builder import build_context
from .llm_service import ask_llm
from .smart_recommendation_service import recommend_by_query
from .movie_serializer import serialize_movies

import re

def execute_tool(intent,user,message):

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
            user,
            message
        )
    elif intent == Intent.SIMILAR:
        return similar_movies_tool(
            user,
            message
        )
    elif intent == Intent.PERSONALIZED:
        return personalized_tool(user)
    
    elif intent == Intent.MOVIE_INFO:
        return movie_info_tool(
            user,
            message
        )
    elif intent == Intent.SEARCH:
        return search_tool(
            user,
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
        return actor_tool(user,message)
    elif intent == Intent.DIRECTOR_MOVIES:
        return director_movies_tool(user,message)
    elif intent == Intent.YEAR:
        return year_tool(message)
    
    movie = MovieParser.find_movie(user, message)

    if movie:
        return {
            "type": "movie_info",
            "message": "",
            "movie": serialize_movies([movie])[0]
        }
    
    return {
        "type": "text",
        "message": "I couldn't understand your request."
    }

# Place Holder tools
def recommend_movies_tool(user,message):
    movie = MovieParser.find_movie(user,message)

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

    movies = recommend_by_query(message)

    if movies:
        return {
            "type": "movies",
            "message": "Here are some recommendations for you.",
            "movies": serialize_movies(movies),
        }

    movies = get_top_movies()

    return {
        "type": "movies",
        "message": "Here are some highly rated movies.",
        "movies": serialize_movies(movies),
    }

def similar_movies_tool(user,message):
    movie = MovieParser.find_movie(user, message)
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

    if not user.is_authenticated:
        return {
            "type": "text",
            "message": "Please login to receive personalized recommendations."
        }

    movies = recommend_personalized(
        user,
        top_n=10,
    )

    if not movies:
        return {
            "type": "text",
            "message": (
                "I don't have enough information yet.\n\n"
                "Rate a few movies first so I can personalize recommendations."
            )
        }

    context = build_context(movies)

    answer = ask_llm(
        "Recommend movies for this user based on their watching history.",
        context,
    )

    return {
        "type": "movies",
        "message": answer,
        "movies": serialize_movies(movies),
    }

def movie_info_tool(user,message):
    movie = MovieParser.find_movie(user, message)
    if movie is None:
        movie = MovieParser.get_last_movie(user)

    if movie is None:
        return {
            "type": "text",
            "message": "Which movie are you referring to?"
        }
    msg = message.lower()

    if "director" in msg or "directed" in msg:
        answer = f"{movie.title} was directed by {movie.director}."
    elif any(
        word in msg
        for word in [
            "actor",
            "actors",
            "cast",
            "star",
            "stars",
            "starring",
            "lead"
        ]
    ):
        answer = (
            f"The main cast includes {movie.actors}"
            if movie.actors
            else "Cast information is not available."
        )
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
                if movie.release_date else ""
            ),
            "genres": movie.genres,
            "overview": movie.overview,
            "director": movie.director,
            "actors": movie.actors,
        },

        "actions": [
            {
                "id": "similar",
                "label": "🎥 Similar Movies",
            },
            {
                "id": "director_movies",
                "label": "🎬 More by this Director",
            },
            {
                "id": "cast",
                "label": "🎭 Full Cast",
            },
            {
                "id": "watchlist",
                "label": "➕ Add to Watchlist",
            },
            {
                "id": "rate",
                "label": "⭐ Rate Movie",
            },
        ]
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

def search_tool(user, message):

    query = re.sub(
        r"\b(find|search|show)\b",
        "",
        message,
        flags=re.IGNORECASE,
    ).strip()

    if not query:
        return {
            "type": "text",
            "message": "Please tell me which movie you want to search."
        }

    movie = MovieParser.find_movie(user, query)

    if movie:
        return {
            "type": "movies",
            "message": "I found this movie.",
            "movies": serialize_movies([movie]),
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
        "movies": serialize_movies(movies),
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

def actor_tool(user, message):

    movie = MovieParser.find_movie(user, message)

    if movie:
        return {
            "type": "movie_info",
            "message": (
                f"The main cast of {movie.title} includes:\n\n{movie.actors}"
                if movie.actors
                else "Cast information is not available."
            ),
            "movie": serialize_movies([movie])[0],
        }

    movie = MovieParser.get_last_movie(user)

    if movie:
        return {
            "type": "text",
            "message": (
                f"The main cast of {movie.title} includes:\n\n{movie.actors}"
                if movie.actors
                else "Cast information is not available."
            ),
        }

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

def director_movies_tool(user, message):
    msg = message.lower()

    # -------------------------------------------------
    # Context-aware queries
    # -------------------------------------------------

    if any(
        phrase in msg
        for phrase in [
            "same director",
            "another one",
            "more by this director",
            "his movies",
            "her movies",
        ]
    ):
        movie = MovieParser.get_last_movie(user)
        if not movie:
            return {
                "type": "text",
                "message": "Which movie are you referring to?"
            }
        director = movie.director
        if not director:
            return {
                "type": "text",
                "message": "I don't know who directed that movie."
            }

    else:
        director = re.sub(
            r"(movies?|films?|directed\s+by|movies\s+by|films\s+by|director)",
            "",
            message,
            flags=re.IGNORECASE,
        )

        director = re.sub(r"\s+", " ", director).strip()

    movies = get_movies_by_director(director)
    current_movie = MovieParser.get_last_movie(user)

    if current_movie:
        movies = [
            m for m in movies
            if m.id != current_movie.id
        ]

    if not movies:
        return {
            "type": "text",
            "message": f"No movies found for {director}."
        }

    return {
        "type": "movies",
        "message": f"Movies directed by {director}",
        "movies": serialize_movies(movies),
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