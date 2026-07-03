import os

from langchain_chroma import Chroma

from apps.chatbot.services.embeddings_service import (
    get_embeddings,
)

VECTOR_DB_PATH = os.path.join(
    "vector_store",
    "chroma_db",
)


def get_vector_store():

    return Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=get_embeddings(),
    )


def similarity_search(
    query,
    k=5,
):

    vector_store = get_vector_store()

    return vector_store.similarity_search(
        query,
        k=k,
    )