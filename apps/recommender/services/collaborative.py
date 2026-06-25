import joblib
from apps.movies.models import Movie

model = joblib.load(
    "ml_models/collaborative_model.joblib"
)

user_movie_matrix = joblib.load(
    "ml_models/user_movie_matrix.joblib"
)


def recommend_collaborative(
    title,
    top_n=10
):

    movie = Movie.objects.filter(
        title=title
    ).first()

    if not movie:
        return []

    movie_id = movie.movie_id

    try:

        movie_row = user_movie_matrix.loc[
            movie_id
        ]

    except KeyError:

        return []

    distances, indices = model.kneighbors(
        [movie_row],
        n_neighbors=top_n + 1
    )

    recommended_movies = []

    for idx in indices.flatten()[1:]:

        recommended_movie_id = (
            user_movie_matrix.index[idx]
        )

        recommended_movie = Movie.objects.filter(
            movie_id=recommended_movie_id
        ).first()

        if recommended_movie:

            recommended_movies.append(
                recommended_movie
            )

    return recommended_movies