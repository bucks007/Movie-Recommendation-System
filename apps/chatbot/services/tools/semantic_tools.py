from langchain_core.tools import tool
from ..semantic_search_service import semantic_search

@tool
def semantic_movie_search(query: str):
    """
    Search movies using semantic similarity.
    """

    docs = semantic_search(query, k=5)

    return "\n\n".join(
        doc.page_content
        for doc in docs
    )