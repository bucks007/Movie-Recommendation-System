import os

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


llm = ChatGoogleGenerativeAI(

    model="gemini-3.5-flash",

    google_api_key=os.getenv("GEMINI_API_KEY"),

    temperature=0.3,
)


def ask_llm(
    question,
    context,
):

    prompt = f"""
        You are an expert movie recommendation assistant.

        You must answer ONLY using the provided movie information.

        If multiple movies match, mention all relevant ones.

        If no movie matches the user's request, say:

        "I couldn't find a movie matching that description."

        Never invent movies.

        ========================

        Movie Database

        {context}

        ========================

        User Question

        {question}

        Answer in a friendly conversational style.
        """

    response = llm.invoke(prompt)

    if isinstance(response.content, list):
        return "".join(
            block.get("text", "")
            for block in response.content
            if isinstance(block, dict)
        )

    return response.content