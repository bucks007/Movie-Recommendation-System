from langchain_core.tools import tool

@tool
def chatbot_help():
    """
    Explain chatbot abilities.
    """

    return (
        "I can recommend movies, search movies, "
        "find actors, directors and explain plots."
    )