import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from google.genai.errors import ServerError
from .memory_service import get_memory
from .prompt_template import prompt
from .parser_service import parser

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3,
)

chain = prompt | llm | parser

def ask_llm(user,question, context):
    memory = get_memory(user)

    history_text = ""

    for msg in memory.messages:

        role = (
            "User"
            if msg.type == "human"
            else "Assistant"
        )

        history_text += (
            f"{role}: {msg.content}\n"
        )
    try:
        answer = chain.invoke(
            {
                "question": question,
                "context": context,
                "history": history_text,
            }
        )

        memory.add_user_message(question)
        memory.add_ai_message(answer)

        return answer
    
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