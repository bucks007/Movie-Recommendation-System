from .query_rewriter import rewrite_query
from .chroma_service import get_retriever


def semantic_search(query, k=12):
    rewritten_query = query
    retriever = get_retriever(k)
    docs = retriever.invoke(rewritten_query)

    return docs