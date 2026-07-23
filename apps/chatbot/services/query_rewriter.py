from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .llm_service import llm
from .memory_store import get_session_history
from .conversation_rewriter import rewrite_from_memory


rewrite_prompt = ChatPromptTemplate.from_template(
"""
You are a query rewriting assistant.

Rewrite the user's latest question into a standalone question.

Use the previous conversation only if needed.

Do NOT answer the question.

Conversation History:
{history}

Current Question:
{question}

Standalone Question:
"""
)

rewrite_chain = (
    rewrite_prompt
    | llm
    | StrOutputParser()
)


def rewrite_query(user, query):
    query = rewrite_from_memory(
        user,
        query
    )
    history = get_session_history(str(user.id))

    history_text = "\n".join(
        f"{msg.type}: {msg.content}"
        for msg in history.messages
    )

    # No previous conversation
    if not history_text.strip():
        return query

    rewritten = rewrite_chain.invoke(
        {
            "history": history_text,
            "question": query,
        }
    )

    print("\n" + "=" * 80)
    print("Original :", query)
    print("Rewritten:", rewritten)
    print("=" * 80 + "\n")

    return rewritten