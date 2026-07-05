from apps.movies.models import Movie
from .intent_service import Intent
from .tool_service import execute_tool

from .chroma_service import search_movies
from .llm_service import ask_llm


STRUCTURED_INTENTS = {

    Intent.GENRE,

    Intent.ACTOR,

    Intent.DIRECTOR_MOVIES,

    Intent.YEAR,

    Intent.TOP_RATED,

    Intent.TRENDING,

    Intent.LATEST,

}


SEMANTIC_INTENTS = {

    Intent.RECOMMEND,

    Intent.SIMILAR,

    Intent.MOVIE_INFO,

    Intent.SEARCH,

    Intent.UNKNOWN,

}


def orchestrate(user, intent, message):

    # -----------------------
    # Structured Tool
    # -----------------------

    if intent in STRUCTURED_INTENTS:

        return execute_tool(
            intent,
            user,
            message,
        )

    # -----------------------
    # Semantic Search
    # -----------------------

    if intent in SEMANTIC_INTENTS:

        docs = search_movies(
            message,
            k=5,
        )

        context = "\n\n".join(
            doc.page_content
            for doc in docs
        )

        answer = ask_llm(
            message,
            context,
        )

        movie_ids = [
            doc.metadata["movie_id"]
            for doc in docs
        ]

        movies = list(
            Movie.objects.filter(
                movie_id__in=movie_ids
            )
        )

        return {
            "type": "movies",
            "message": answer,
            "movies": execute_tool.serialize_movies(movies)
        }

    return execute_tool(
        intent,
        user,
        message,
    )