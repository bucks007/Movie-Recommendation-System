from apps.movies.models import Movie
from .intent_service import Intent
from .tool_service import execute_tool

from .movie_serializer import serialize_movies
from .semantic_search_service import semantic_search
from .llm_service import ask_llm
from .context_builder import build_context

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

        docs = semantic_search(
            query=message,
            k=8,
        )

        movie_ids = list({
            doc.metadata["movie_id"]
            for doc in docs
        })

        movies = list(
            Movie.objects.filter(
                movie_id__in=movie_ids,
                vote_average__gte=6,
            ).exclude(
                release_date__isnull=True
            )
        )

        context = build_context(movies)

        answer = ask_llm(
            message,
            context,
        )

        return {
            "type": "movies",
            "message": answer,
            "movies": serialize_movies(movies)
        }

    return execute_tool(
        intent,
        user,
        message,
    )