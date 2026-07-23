# Movie Recommender: LLM, Tools, LangChain, RAG, and Data Flow

This document describes how the AI chatbot, LLM, tools, LangChain pipeline, semantic search, and recommendation logic are connected in this `movie_recommender` Django project.

It is based on the current code inside:

- `apps/chatbot/`
- `apps/recommender/`
- `apps/movies/`
- `vector_store/`
- `ml_models/`

## 1. Project-Level Architecture

The project is a Django movie recommendation system with an AI chatbot layer.

The main backend areas are:

| Area | Purpose |
|---|---|
| `apps/movies` | Stores movie data, ratings, watchlists, and normal movie pages |
| `apps/recommender` | Content-based, collaborative, hybrid, and personalized recommendation logic |
| `apps/chatbot` | Chatbot API, LangChain pipeline, LLM calls, tools, memory, RAG, semantic search |
| `ml_models` | Saved joblib ML models for recommendation similarity |
| `vector_store/chroma_db` | Chroma vector database for semantic movie search |
| `datasets/ml-latest-small` | MovieLens source dataset files |

The chatbot is not just a direct LLM call. It combines:

- Django request handling
- LangChain runnable pipeline
- Intent detection
- Query rewriting
- Gemini LLM
- Chroma vector search
- Hugging Face embeddings
- Django ORM queries
- ML recommendation models
- In-memory chat history
- Frontend movie cards

## 2. Active Chatbot Request Flow

The active web flow starts from the browser chatbot widget.

```text
Browser chatbot UI
  |
  v
POST /chatbot/send/
  |
  v
apps.chatbot.views.chat_message
  |
  v
apps.chatbot.services.chat_service.process_message
  |
  v
chat_pipeline.invoke(...)
  |
  v
LangChain runnable pipeline
  |
  v
Tool result / LLM result
  |
  v
JsonResponse
  |
  v
chatbot.js renders text, movie cards, or movie-info card
```

Route files:

- `config/urls.py` includes `apps.chatbot.urls` at `/chatbot/`.
- `apps/chatbot/urls.py` maps `/chatbot/send/` to `chat_message`.
- `apps/chatbot/views.py` receives JSON and returns JSON.
- `apps/chatbot/static/chatbot/chatbot.js` sends the request and renders the response.

## 3. Frontend to Backend Flow

The chatbot frontend is in:

```text
apps/chatbot/static/chatbot/chatbot.js
```

When the user sends a message:

```javascript
fetch("/chatbot/send/", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken")
    },
    body: JSON.stringify({
        message: message
    })
})
```

The backend returns one of these response shapes:

```json
{
  "type": "text",
  "message": "Text answer"
}
```

```json
{
  "type": "movies",
  "message": "Recommendation explanation",
  "movies": [
    {
      "id": 1,
      "movie_id": 260,
      "title": "Star Wars",
      "poster": "https://...",
      "rating": 8.6,
      "genres": "Action, Adventure",
      "year": 1977
    }
  ]
}
```

```json
{
  "type": "movie_info",
  "movie": {
    "id": 1,
    "title": "Movie title",
    "poster": "https://...",
    "rating": 8.2,
    "year": 2010,
    "genres": "Sci-Fi",
    "overview": "Movie overview",
    "director": "Director name",
    "actors": "Actor names"
  }
}
```

The frontend checks `data.type`:

- `movie_info` -> renders one detailed movie card.
- `movies` -> renders an assistant message and multiple movie cards.
- anything else -> renders plain bot text.

## 4. Active LangChain Pipeline

The active pipeline is defined in:

```text
apps/chatbot/services/chat_pipeline.py
```

The pipeline is:

```python
chat_pipeline = (
    rewrite_runnable
    | intent_runnable
    | chat_branch
)
```

This means every chatbot message goes through three stages:

```text
Input message
  |
  v
rewrite_runnable
  |
  v
intent_runnable
  |
  v
chat_branch
  |
  v
Final JSON response
```

### 4.1 Pipeline Input

`process_message` sends this input into the pipeline:

```python
{
    "user": user,
    "message": message,
}
```

It also passes a configurable `session_id`:

```python
config={
    "configurable": {
        "session_id": str(user.id)
    }
}
```

## 5. Query Rewriting

The first pipeline step is `rewrite_runnable`.

File:

```text
apps/chatbot/services/query_rewriter.py
```

Purpose:

- Converts follow-up questions into standalone questions.
- Uses previous chat history when available.
- Uses Gemini through the shared `llm` object.

Example:

```text
User: Tell me about Inception
Assistant: ...
User: Who directed it?
```

The query rewriter can turn:

```text
Who directed it?
```

into:

```text
Who directed Inception?
```

Current implementation:

```python
rewrite_chain = (
    rewrite_prompt
    | llm
    | StrOutputParser()
)
```

It uses:

- `ChatPromptTemplate`
- Gemini LLM
- `StrOutputParser`
- `get_session_history(str(user.id))`

Important detail: the rewritten query is stored as `x["query"]`, but intent detection still uses the original `x["message"]`.

## 6. Intent Detection

The second pipeline step is `intent_runnable`.

File:

```text
apps/chatbot/services/intent_service.py
```

Intent detection is rule-based using Python regex. It does not use the LLM.

Supported intents:

| Intent | Example user input |
|---|---|
| `GREETING` | "hello" |
| `HELP` | "what can you do" |
| `PERSONALIZED` | "recommend me movies" |
| `TRENDING` | "show trending movies" |
| `TOP_RATED` | "top rated movies" |
| `LATEST` | "latest movies" |
| `SIMILAR` | "movies like Inception" |
| `ACTOR` | "movies starring Tom Hanks" |
| `DIRECTOR_MOVIES` | "movies by Nolan" |
| `YEAR` | "movies from 2010" |
| `RECOMMEND` | "suggest good movies" |
| `GENRE` | "action movies" |
| `MOVIE_INFO` | "tell me about Interstellar" |
| `SEARCH` | "find Avatar" |
| `UNKNOWN` | fallback |

Flow:

```text
Message text
  |
  v
Lowercase and strip
  |
  v
Regex checks
  |
  v
Intent enum value
```

## 7. LangChain Branching Logic

The third pipeline step is `chat_branch`.

File:

```text
apps/chatbot/services/chat_pipeline.py
```

Branch logic:

```text
If intent is RECOMMEND or SIMILAR
  -> recommendation_runnable

If intent is MOVIE_INFO, SEARCH, ACTOR, or DIRECTOR_MOVIES
  -> tool_runnable

Otherwise
  -> tool_runnable
```

So in the active chatbot path:

- Recommendation-like messages use `smart_recommend` + LLM answer generation.
- Most structured questions use `execute_tool`.
- The fallback also uses `execute_tool`.

## 8. LLM Configuration

The project uses Gemini through LangChain.

File:

```text
apps/chatbot/services/llm_service.py
```

Current LLM:

```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3,
)
```

The API key is loaded from environment variables using:

```python
load_dotenv()
os.getenv("GEMINI_API_KEY")
```

The LLM is used for:

- Query rewriting
- Final natural-language answers for recommendations
- RAG-style answer generation
- Optional LangChain agent execution

The LLM is not responsible for directly searching the database. It receives context that was fetched by tools, retrievers, or recommendation services.

## 9. Prompt and Output Parser

The main LLM chain is in:

```text
apps/chatbot/services/llm_service.py
```

```python
chain = prompt | llm | parser
```

The prompt comes from:

```text
apps/chatbot/services/prompt_template.py
apps/chatbot/services/prompt_builder.py
apps/chatbot/prompt/system_prompt.txt
apps/chatbot/prompt/movie_prompt.txt
```

The parser is:

```text
apps/chatbot/services/parser_service.py
```

Current parser:

```python
parser = StrOutputParser()
```

So the LLM output is parsed as plain text.

## 10. Conversation Memory

There are two memory-related implementations in the project.

### 10.1 Main LLM Memory

File:

```text
apps/chatbot/services/memory_service.py
```

This uses:

```python
ChatMessageHistory
```

Memory is stored in a Python dictionary:

```python
memory_store = {}
```

Key behavior:

- Authenticated users use `str(user.id)` as the memory key.
- Anonymous users use `"anonymous"`.
- The memory is in-process only.
- It is lost when the server restarts.

The `ask_llm` function reads previous messages, formats them as text, sends them to the prompt, then adds the new user and AI messages.

### 10.2 Query Rewriter State and Last Movie State

File:

```text
apps/chatbot/services/memory_store.py
```

This stores:

- `history_store` for query rewriting
- `state_store` for state like `last_movie_id`

`MovieParser` uses `state_store` so a follow-up like "who directed it?" can refer to the last movie.

Important detail: `memory_service.py` and `memory_store.py` are separate memory stores. They do not automatically sync with each other.

## 11. Recommendation Path in Active Pipeline

For `RECOMMEND` and `SIMILAR` intents, the active path is:

```text
User message
  |
  v
rewrite_query
  |
  v
detect_intent
  |
  v
recommendation_node
  |
  v
smart_recommend(user, rewritten_query, top_n=10)
  |
  v
build_context(movies)
  |
  v
ask_llm(user, rewritten_query, context)
  |
  v
serialize_movies(movies)
  |
  v
JSON response with type = "movies"
```

The important function is:

```text
apps/chatbot/services/smart_recommendation_engine.py
```

`smart_recommend` combines multiple signals:

1. Semantic search from Chroma
2. Personalized recommendations for logged-in users
3. Content-based recommendations from saved joblib similarity model
4. IMDb rating score
5. Filtering out already rated movies for authenticated users

Scoring logic:

```text
Semantic search result score: 30 - rank
Personalized result score:   25 - rank
Content-based result score:  15 - rank
Final sorting also adds:     vote_average / 2
```

## 12. Semantic Search and Chroma Vector Store

Semantic search is used in:

```text
apps/chatbot/services/semantic_search_service.py
apps/chatbot/services/chroma_service.py
apps/chatbot/services/smart_recommendation_engine.py
```

Flow:

```text
User query
  |
  v
Hugging Face embedding model
  |
  v
Chroma vector database
  |
  v
Top matching movie documents
  |
  v
Movie IDs from document metadata
  |
  v
Django ORM fetches Movie rows
```

The vector database path is:

```text
vector_store/chroma_db
```

The embedding model is:

```python
sentence-transformers/all-mpnet-base-v2
```

Defined in:

```text
apps/chatbot/services/embeddings_service.py
```

Chroma setup:

```python
Chroma(
    persist_directory="vector_store/chroma_db",
    embedding_function=get_embeddings(),
)
```

The retriever uses similarity search:

```python
as_retriever(
    search_type="similarity",
    search_kwargs={"k": k}
)
```

## 13. How the Vector Database Is Built

The vector database is built by the management command:

```text
apps/chatbot/management/commands/build_vector_db.py
```

Command:

```powershell
python manage.py build_vector_db
```

Build flow:

```text
Movie.objects.all()
  |
  v
For each movie with a useful overview
  |
  v
Create LangChain Document
  |
  v
Add page_content with title, overview, genres, themes, director, actors, year, rating
  |
  v
Add metadata with movie_id, title, genres, director, year, vote_average
  |
  v
Embed documents in batches
  |
  v
Store vectors in Chroma
```

Each Chroma document includes searchable movie text like:

- Movie title
- Overview
- Genres
- Theme keywords
- Director
- Actors
- Release year
- IMDb rating

Metadata includes:

```python
{
    "movie_id": movie.movie_id,
    "title": movie.title,
    "genres": movie.genres,
    "director": movie.director,
    "year": movie.release_date.year,
    "vote_average": movie.vote_average,
}
```

This is how semantic queries like "mind bending space movie" can find relevant movies even if the exact title is not present in the user message.

## 14. Database Data Used by Tools

The main movie data model is:

```text
apps/movies/models.py
```

Main models:

- `Movie`
- `Rating`
- `Watchlist`

Important `Movie` fields:

- `movie_id`
- `imdb_id`
- `tmdb_id`
- `title`
- `overview`
- `genres`
- `director`
- `actors`
- `runtime`
- `release_date`
- `poster_url`
- `backdrop_url`
- `vote_average`
- `popularity`

The tools and recommendation services fetch data using Django ORM queries such as:

```python
Movie.objects.filter(title__icontains=query)
Movie.objects.filter(genres__icontains=genre)
Movie.objects.filter(actors__icontains=actor)
Movie.objects.filter(director__icontains=director)
Movie.objects.filter(release_date__year=year)
Movie.objects.order_by("-vote_average")
```

## 15. Tool Service

The structured tool router is:

```text
apps/chatbot/services/tool_service.py
```

The main function is:

```python
execute_tool(intent, user, message)
```

It routes the detected intent to a normal Python function.

Tool mapping:

| Intent | Tool function | Data source |
|---|---|---|
| `GREETING` | direct text response | static text |
| `HELP` | direct text response | static text |
| `RECOMMEND` | `recommend_movies_tool` | MovieParser, content-based model, query recommendation, top movies |
| `SIMILAR` | `similar_movies_tool` | MovieParser, content-based model |
| `PERSONALIZED` | `personalized_tool` | user ratings, hybrid recommender |
| `MOVIE_INFO` | `movie_info_tool` | MovieParser, Movie model |
| `SEARCH` | `search_tool` | MovieParser, Movie title search |
| `GENRE` | `genre_tool` | Movie genre filter |
| `TRENDING` | `trending_tool` | rating and release-date ordering |
| `TOP_RATED` | `top_rated_tool` | rating ordering |
| `LATEST` | `latest_tool` | release-date ordering |
| `ACTOR` | `actor_tool` | actor filter |
| `DIRECTOR_MOVIES` | `director_movies_tool` | director filter |
| `YEAR` | `year_tool` | release year filter |

These are "tools" in the project sense, but most active tools are regular Python functions, not LangChain `@tool` functions.

## 16. Movie Parsing and Fuzzy Search

File:

```text
apps/chatbot/services/movie_parser.py
```

`MovieParser.find_movie(user, message)` identifies a movie from user text.

It uses three search levels:

```text
Clean user query
  |
  v
Exact title match
  |
  v
Partial title match
  |
  v
RapidFuzz fuzzy match
```

It also stores the matched movie as `last_movie_id` in `state_store`.

That allows follow-up messages like:

```text
User: Tell me about Interstellar
User: Show similar movies
```

or:

```text
User: Tell me about Inception
User: Who directed it?
```

## 17. Content-Based Recommendations

File:

```text
apps/recommender/services/content_based.py
```

This service loads saved ML files:

```text
ml_models/cosine_similarity.joblib
ml_models/movie_indices.joblib
ml_models/movie_ids.joblib
```

Flow:

```text
Seed movie_id
  |
  v
Find movie index from movie_indices.joblib
  |
  v
Read similarity row from cosine_similarity.joblib
  |
  v
Sort by similarity score
  |
  v
Get top movie_ids
  |
  v
Fetch Movie rows from database
  |
  v
Return ordered movie list
```

This is used by:

- `similar_movies_tool`
- `recommend_movies_tool`
- `smart_recommend`
- hybrid recommender

## 18. Collaborative Recommendations

File:

```text
apps/recommender/services/collaborative.py
```

This service loads:

```text
ml_models/collaborative_model.joblib
ml_models/user_movie_matrix.joblib
```

Flow:

```text
Movie title
  |
  v
Find Movie row
  |
  v
Get movie_id
  |
  v
Get vector row from user_movie_matrix
  |
  v
Use nearest-neighbor model
  |
  v
Convert neighbor movie IDs to Movie rows
```

## 19. Hybrid and Personalized Recommendations

Hybrid service:

```text
apps/recommender/services/hybrid.py
```

It combines:

- content-based recommendations
- collaborative recommendations

Personalized service:

```text
apps/recommender/services/personalized.py
```

Flow:

```text
Logged-in user
  |
  v
Fetch top 5 user ratings
  |
  v
For each highly rated movie
  |
  v
Call hybrid recommender
  |
  v
Remove already rated movies
  |
  v
Return top recommendations
```

This depends on:

```text
apps.movies.models.Rating
```

## 20. LLM Answer Generation for Recommendations

When movies are found through `smart_recommend`, the project does not return only raw movie cards. It also asks the LLM to write a natural-language answer.

Flow:

```text
Recommended Movie objects
  |
  v
build_context(movies)
  |
  v
Prompt receives:
    - conversation history
    - movie instructions
    - movie context
    - user question
  |
  v
Gemini generates answer
  |
  v
Response JSON includes answer + serialized movie cards
```

The context builder includes:

- title
- genres
- director
- actors
- overview
- IMDb rating
- release date

File:

```text
apps/chatbot/services/context_builder.py
```

## 21. RAG Chain

There is a RAG chain in:

```text
apps/chatbot/services/rag_chain.py
```

It uses:

- Chroma retriever
- `ChatPromptTemplate`
- Gemini LLM
- `StrOutputParser`

Flow:

```text
Question
  |
  v
Retriever searches Chroma
  |
  v
format_docs joins document page content
  |
  v
Prompt receives context and question
  |
  v
LLM answers only using provided context
```

Current chain:

```python
rag_chain = (
    {
        "context": itemgetter("question") | retriever | format_docs,
        "question": itemgetter("question"),
    }
    | prompt
    | llm
    | StrOutputParser()
)
```

Important current-code note: `rag_chain` is imported in `orchestrator.py`, but the active `chat_service` path uses `chat_pipeline`, not `orchestrator.orchestrate`.

## 22. LangChain Agent File

There is also an agent implementation in:

```text
apps/chatbot/services/agent_service.py
```

It creates:

```python
AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    return_intermediate_steps=True,
)
```

It uses:

- `ChatGoogleGenerativeAI`
- `create_tool_calling_agent`
- `langchain.hub.pull("hwchase17/openai-tools-agent")`
- LangChain tool functions from `apps/chatbot/services/tools/`

Registered agent tools include:

- `recommend_by_genre`
- `top_movies`
- `search_movies`
- `movie_information`
- `semantic_movie_search`
- `personalized_recommendations`
- `recommend_movies`
- `chatbot_help`

Important current-code note: this agent is not the active path for `/chatbot/send/`. The active endpoint calls `process_message`, which invokes `chat_pipeline`, not `run_agent`.

## 23. LangChain Tool Files

The LangChain tool-style files are in:

```text
apps/chatbot/services/tools/
```

Files:

- `general_tools.py`
- `hybrid_tools.py`
- `movie_info_tools.py`
- `personalized_tools.py`
- `recommendation_tools.py`
- `search_tools.py`
- `semantic_tools.py`

These are used by `agent_service.py`. They are separate from the active `execute_tool` router.

So the project currently has two tool concepts:

| Tool type | Used by | Active web path? |
|---|---|---|
| Python router tools in `tool_service.py` | `chat_pipeline` | Yes |
| LangChain tool functions in `services/tools/` | `agent_service.py` | Not through `/chatbot/send/` currently |

## 24. Complete Active Flow Example: Similar Movie Query

User:

```text
Recommend movies similar to Inception
```

Flow:

```text
chatbot.js
  |
  v
POST /chatbot/send/
  |
  v
chat_message(request)
  |
  v
process_message(user, message)
  |
  v
chat_pipeline.invoke(...)
  |
  v
rewrite_query(...)
  |
  v
detect_intent(...) -> Intent.SIMILAR
  |
  v
recommendation_node
  |
  v
smart_recommend(user, rewritten_query)
  |
  +--> semantic_search(query)
  |       |
  |       v
  |     Chroma retriever returns movie docs
  |
  +--> recommend_personalized(user), if logged in
  |
  +--> content_based.recommend_movies(seed_movie)
  |
  v
Rank movie IDs
  |
  v
Movie.objects.filter(movie_id__in=movie_ids)
  |
  v
build_context(movies)
  |
  v
ask_llm(user, question, context)
  |
  v
serialize_movies(movies)
  |
  v
JSON response
  |
  v
Frontend renders answer and cards
```

## 25. Complete Active Flow Example: Search Movie

User:

```text
Find Avatar
```

Flow:

```text
chat_pipeline
  |
  v
detect_intent -> Intent.SEARCH
  |
  v
tool_runnable
  |
  v
execute_tool(Intent.SEARCH, user, message)
  |
  v
search_tool(user, message)
  |
  v
MovieParser.find_movie(user, query)
  |
  +--> exact title match
  +--> partial title match
  +--> RapidFuzz fuzzy match
  |
  v
If movie found:
    return type = "movies" with one serialized movie
  |
  v
If not found:
    Movie.objects.filter(title__icontains=query)
```

In this path, the LLM is not required. It is a direct database/tool response.

## 26. Complete Active Flow Example: Movie Information

User:

```text
Tell me about Interstellar
```

Flow:

```text
detect_intent -> MOVIE_INFO
  |
  v
execute_tool
  |
  v
movie_info_tool
  |
  v
MovieParser.find_movie
  |
  v
Build movie_info JSON object
  |
  v
Frontend renders detailed card
```

If the message asks for a specific field:

- director
- actors
- plot
- runtime
- rating
- release date
- genre
- year

the tool generates a direct answer from the `Movie` model.

## 27. How Data Is Fetched

This project fetches data from five main places.

### 27.1 SQLite Database

The Django database stores:

- movies
- ratings
- watchlists
- users

Most structured tools fetch from the database using Django ORM.

### 27.2 Chroma Vector Database

Chroma stores embedded movie documents.

Used for:

- semantic search
- smart recommendation ranking
- RAG chain context retrieval

### 27.3 Joblib ML Models

Saved models in `ml_models` support:

- content-based similarity
- collaborative nearest-neighbor recommendations
- movie ID mappings

### 27.4 Prompt Text Files

The chatbot loads prompt instructions from:

```text
apps/chatbot/prompt/system_prompt.txt
apps/chatbot/prompt/movie_prompt.txt
```

These files control the LLM's behavior and movie-answer style.

### 27.5 Environment Variables

The Gemini API key is read from:

```text
.env
```

Expected variable:

```text
GEMINI_API_KEY
```

## 28. Current Code Notes and Risks

These notes are based on the current source code.

### 28.1 Active Path vs Orchestrator

`orchestrator.py` exists, but the active `/chatbot/send/` endpoint uses:

```text
chat_service.py -> chat_pipeline.py
```

So the main runtime path is the LangChain runnable pipeline, not `orchestrator.orchestrate`.

### 28.2 Active Tools Are Mostly Plain Python Tools

The active tools in `tool_service.py` are normal Python functions selected by `execute_tool`.

The LangChain agent tools under `services/tools/` are used by `agent_service.py`, but that agent is not currently connected to the active chatbot endpoint.

### 28.3 Some Function Calls Appear Inconsistent

In `llm_service.py`, the function signature is:

```python
def ask_llm(user, question, context):
```

Some older code paths call it with fewer or different arguments. For example, parts of `tool_service.py`, `orchestrator.py`, and `rag_service.py` appear inconsistent with that signature.

The active recommendation node in `chat_pipeline.py` correctly calls:

```python
ask_llm(x["user"], x["query"], context)
```

### 28.4 `rag_service.py` Has a Likely Bug

`rag_service.py` calls:

```python
return ask_llm(
    users,
    question,
    context
)
```

but `users` is not defined in that file. This suggests `rag_service.py` is currently not the active production path.

### 28.5 In-Memory State Is Temporary

Chat memory and last-movie state are stored in Python dictionaries. This is simple, but:

- data resets when the Django server restarts
- memory is not shared across multiple server processes
- anonymous users share the `"anonymous"` key in `memory_service.py`

## 29. Summary Diagram

```text
User
  |
  v
Chatbot UI
  |
  v
/chatbot/send/
  |
  v
Django view: chat_message
  |
  v
process_message
  |
  v
LangChain chat_pipeline
  |
  +--> Query rewriting with Gemini
  |
  +--> Regex intent detection
  |
  +--> Branch:
        |
        +--> Recommendation path
        |       |
        |       +--> Chroma semantic search
        |       +--> personalized recommender
        |       +--> content-based recommender
        |       +--> Django ORM movie fetch
        |       +--> Gemini answer generation
        |
        +--> Tool path
                |
                +--> MovieParser
                +--> Django ORM queries
                +--> recommendation services
                +--> direct JSON response
  |
  v
JsonResponse
  |
  v
Frontend renders text/cards
```

## 30. Short Final Explanation

In this project, LangChain is mainly used to organize the chatbot pipeline and LLM chains. The LLM is Gemini `gemini-2.5-flash`, called through `ChatGoogleGenerativeAI`. The tools are mostly project-specific Python functions that search movies, fetch details, and run recommendation services. Semantic search uses Hugging Face embeddings with Chroma. The recommendation system combines semantic search, saved joblib ML models, user ratings, and Django ORM queries.

The LLM does not fetch data directly from the database. The code fetches data through tools, retrievers, Django ORM, Chroma, and ML services, then passes selected context into the LLM so it can generate a human-readable movie response.
