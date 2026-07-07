from langchain_core.prompts import ChatPromptTemplate

from .prompt_builder import (
    SYSTEM_PROMPT,
    MOVIE_PROMPT,
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            SYSTEM_PROMPT,
        ),
        (
            "human",
            """
Previous Conversation:

{history}

--------------------------------

Movie Instructions:

"""
            + MOVIE_PROMPT
            + """

--------------------------------

Context:

{context}

--------------------------------

Question:

{question}
"""
        ),
    ]
)