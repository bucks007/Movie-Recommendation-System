from apps.movies.models import Movie

from .intent_service import Intent
from .smart_recommendation_engine import smart_recommend
from .tool_service import execute_tool
from .movie_serializer import serialize_movies
from .context_builder import build_context
from .llm_service import ask_llm
from .rag_chain import rag_chain

STRUCTURED_INTENTS = {
    Intent.GENRE,
    Intent.ACTOR,
    Intent.DIRECTOR_MOVIES,
    Intent.YEAR,
    Intent.TOP_RATED,
    Intent.TRENDING,
    Intent.LATEST,
}

RECOMMENDATION_INTENTS = {
    Intent.RECOMMEND,
    Intent.SIMILAR,
    Intent.PERSONALIZED,
}

SEMANTIC_INTENTS = {
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
    # Smart Recommendation
    # -----------------------

    if intent in RECOMMENDATION_INTENTS:

        movies = smart_recommend(
            user=user,
            query=message,
            top_n=10,
        )

        context = build_context(movies)

        answer = ask_llm(
            question=message,
            context=context,
        )

        return {
            "type": "movies",
            "message": answer,
            "movies": serialize_movies(movies),
        }

    # -----------------------
    # Semantic Search
    # -----------------------

    if intent in SEMANTIC_INTENTS:
        movies = smart_recommend(
            user=user,
            query=message,
            top_n=10,
        )

        context = build_context(movies)

        answer = ask_llm(
            message,
            context,
        )

        return {
            "type": "movies",
            "message": answer,
            "movies": serialize_movies(movies),
        }

    return execute_tool(
        intent,
        user,
        message,
    )