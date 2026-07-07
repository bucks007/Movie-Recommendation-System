from collections import defaultdict

from apps.movies.models import Movie
from apps.recommender.services.content_based import (recommend_movies,)
from apps.recommender.services.personalized import (recommend_personalized,)
from .semantic_search_service import semantic_search

def smart_recommend(
    user,
    query,
    top_n=10,
):
    """
    Combines:

    - Semantic Search
    - Content Based
    - Collaborative
    - IMDb score

    Returns ranked Movie queryset.
    """

    scores = defaultdict(float)

    # -----------------------------
    # Semantic Search
    # -----------------------------

    docs = semantic_search(
        query=query,
        k=10,
    )

    for rank, doc in enumerate(docs):
        movie_id = doc.metadata["movie_id"]
        scores[movie_id] += 30 - rank

    # -----------------------------
    # Personalized
    # -----------------------------

    if user.is_authenticated:
        try:
            movies = recommend_personalized(
                user,
                top_n=10,
            )
            for rank, movie in enumerate(movies):
                scores[movie.movie_id] += 25 - rank
        except Exception:
            pass

    # -----------------------------
    # Content Based
    # -----------------------------

    if docs:
        seed_movie = docs[0].metadata["movie_id"]
        try:
            similar = recommend_movies(
                seed_movie,
                top_n=8,
            )

            for rank, movie in enumerate(similar):
                scores[movie.movie_id] += 15 - rank
        except Exception:
            pass

    # -----------------------------
    # Final Ranking
    # -----------------------------

    movie_ids = list(scores.keys())
    movies = Movie.objects.filter(
        movie_id__in=movie_ids
    )

    ranked = sorted(
        movies,
        key=lambda m: (
            scores[m.movie_id]
            + (m.vote_average / 2)
        ),
        reverse=True,
    )

    if user.is_authenticated:
        rated_ids = set(
            user.rating_set.values_list(
                "movie__movie_id",
                flat=True,
            )
        )

        ranked = [
            movie
            for movie in ranked
            if movie.movie_id not in rated_ids
        ]

    return ranked[:top_n]