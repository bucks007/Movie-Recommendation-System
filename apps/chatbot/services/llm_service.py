import os

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

from movie_recommender.apps.chatbot.services.prompt_loader import load_prompt

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

    system_prompt = load_prompt("system_prompt.txt")

    movie_prompt = load_prompt("movie_prompt.txt")

    prompt = (
        system_prompt
        + "\n\n"
        + movie_prompt.format(
            context=context,
            question=question,
        )
    )

    response = llm.invoke(prompt)

    if isinstance(response.content, list):
        return "".join(
            block.get("text", "")
            for block in response.content
            if isinstance(block, dict)
        )

    return response.content