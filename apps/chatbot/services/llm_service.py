import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from google.genai.errors import ServerError
from .prompt_builder import build_prompt

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3,
)

def ask_llm(question, context):

    prompt = build_prompt(
        question,
        context,
    )

    try:

        response = llm.invoke(prompt)

    except ServerError:

        return (
            "Sorry, the AI service is currently busy. "
            "Please try again in a few seconds."
        )

    except Exception as e:
        print("=" * 80)
        print(e)
        print("=" * 80)
        return f"Error: {e}"

    if isinstance(response.content, list):

        return "".join(
            block.get("text", "")
            for block in response.content
            if isinstance(block, dict)
        )

    return response.content