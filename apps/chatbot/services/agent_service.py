import os

from dotenv import load_dotenv

from langchain import hub
from langchain.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)

from langchain_google_genai import ChatGoogleGenerativeAI

from .tools.recommendation_tools import (
    recommend_by_genre,
    top_movies,
)

from .tools.search_tools import (
    search_movie,
)

from .tools.movie_info_tools import (
    movie_information,
)

from .tools.semantic_tools import (
    semantic_movie_search,
)

from .tools.general_tools import (
    chatbot_help,
)

load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3,
)

tools = [
    recommend_by_genre,
    top_movies,
    search_movie,
    movie_information,
    semantic_movie_search,
    chatbot_help,
]

prompt = hub.pull("hwchase17/openai-tools-agent")

agent = create_tool_calling_agent(
    llm,
    tools,
    prompt,
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
)

def run_agent(message):

    result = agent_executor.invoke(
        {
            "input": message,
        }
    )

    return result["output"]