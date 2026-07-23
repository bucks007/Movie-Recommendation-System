from langchain_core.runnables import (
    RunnableLambda,
    RunnableBranch,
)

from .query_rewriter import rewrite_query
from .intent_service import detect_intent, Intent
from .smart_recommendation_engine import smart_recommend
from .context_builder import build_context
from .llm_service import ask_llm
from .movie_serializer import serialize_movies
from .tool_service import execute_tool


rewrite_runnable = RunnableLambda(
    lambda x: {
        **x,
        "query": rewrite_query(
            x["user"],
            x["message"]
        )
    }
)

def intent_node(x):
    intent = detect_intent(x["message"])

    print("=" * 60)
    print("Original :", x["message"])
    print("Rewritten:", x["query"])
    print("Intent   :", intent)
    print("=" * 60)

    return {
        **x,
        "intent": intent,
    }

intent_runnable = RunnableLambda(intent_node)

def recommendation_node(x):

    movies = smart_recommend(
        user=x["user"],
        query=x["query"],
        top_n=10,
    )

    context = build_context(
        movies
    )

    answer = ask_llm(
        x["user"],
        x["query"],
        context,
    )

    return {
        "type": "movies",
        "message": answer,
        "movies": serialize_movies(
            movies
        ),
    }


recommendation_runnable = RunnableLambda(
    recommendation_node
)

def tool_node(x):

    return execute_tool(
        x["intent"],
        x["user"],
        x["query"],
    )


tool_runnable = RunnableLambda(
    tool_node
)

semantic_runnable = RunnableLambda(
    recommendation_node
)

chat_branch = RunnableBranch(

    (
        lambda x: x["intent"] in {
            Intent.RECOMMEND,
            Intent.SIMILAR,
        },
        recommendation_runnable,
    ),

    (
        lambda x: x["intent"] in {
            Intent.MOVIE_INFO,
            Intent.SEARCH,
            Intent.ACTOR,
            Intent.DIRECTOR_MOVIES,
        },
        tool_runnable,
    ),

    tool_runnable,
)

chat_pipeline = (

    rewrite_runnable

    | intent_runnable

    | chat_branch

)