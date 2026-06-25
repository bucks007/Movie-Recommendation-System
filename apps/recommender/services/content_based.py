import joblib
import pandas as pd

from apps.movies.models import Movie

cosine_sim = joblib.load(
    "ml_models/cosine_similarity.joblib"
)

indices = joblib.load(
    "ml_models/movie_indices.joblib"
)


def recommend_movies(title, top_n=10):

    if title not in indices:
        return []

    idx = indices[title]

    similarity_scores = list(
        enumerate(cosine_sim[idx])
    )

    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    similarity_scores = similarity_scores[1:top_n + 1]

    movie_indices = [
        score[0]
        for score in similarity_scores
    ]

    movies = list(Movie.objects.all())

    recommended_movies = [
        movies[i]
        for i in movie_indices
    ]

    return recommended_movies