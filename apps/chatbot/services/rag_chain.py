from operator import itemgetter

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .chroma_service import get_retriever
from .llm_service import llm

retriever = get_retriever()


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


prompt = ChatPromptTemplate.from_template(
"""
You are MovieMind AI.

Answer ONLY using the provided context.

Movie Context:
{context}

Question:
{question}

If the answer is not present,
say you don't know.
"""
)

rag_chain = (
    {
        "context": itemgetter("question") | retriever | format_docs,
        "question": itemgetter("question"),
    }
    | prompt
    | llm
    | StrOutputParser()
)