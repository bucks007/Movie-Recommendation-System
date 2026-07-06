from .query_rewriter import rewrite_query
from .chroma_service import search_movies


def semantic_search(query, k=20):

    rewritten_query = rewrite_query(query)

    docs = search_movies(
        rewritten_query,
        k=k,
    )

    return docs