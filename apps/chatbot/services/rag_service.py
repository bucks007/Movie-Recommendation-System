from .chroma_service import get_vector_store
from .llm_service import ask_llm


def rag_answer(question):

    vector_store = get_vector_store()

    results = vector_store.similarity_search_with_score(
        question,
        k=8
    )

    docs = []

    for doc, score in results:

        print("=" * 50)
        print(score)
        print(doc.metadata)

        if score < 1.2:
            docs.append(doc)

    if not docs:
        return "Sorry, I couldn't find any relevant movie."

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    return ask_llm(
        question,
        context
    )