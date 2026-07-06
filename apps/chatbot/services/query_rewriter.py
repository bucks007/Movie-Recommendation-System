import re


def rewrite_query(query: str) -> str:

    query = query.strip()

    # Already contains movie-related words
    movie_words = [
        "movie",
        "film",
        "actor",
        "director",
        "genre",
        "recommend",
        "starring",
    ]

    if any(word in query.lower() for word in movie_words):
        return query

    # Very short queries
    query = query.lower()

    query = query.replace("astronauts", "space astronauts")
    query = query.replace("space survival", "space survival movie")
    query = query.replace("dreams", "dreams subconscious")
    query = query.replace("spirituality", "religion spirituality faith")
    query = query.replace("future", "science fiction future")

    return query