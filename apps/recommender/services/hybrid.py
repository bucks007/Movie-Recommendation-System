from apps.recommender.services.content_based import recommend_movies
from apps.recommender.services.collaborative import recommend_collaborative


def recommend_hybrid(
    movie_title,
    top_n=10
):

    content_recs = recommend_movies(
        movie_title,
        top_n=5
    )

    collab_recs = recommend_collaborative(
        movie_title,
        top_n=5
    )

    combined = []

    seen = set()

    for c, col in zip(
        content_recs,
        collab_recs
    ):

        if c.id not in seen:

            combined.append(c)

            seen.add(c.id)

        if col.id not in seen:

            combined.append(col)

            seen.add(col.id)

    # Add remaining movies
    for movie in content_recs + collab_recs:

        if movie.id not in seen:

            combined.append(movie)

            seen.add(movie.id)

    return combined[:top_n]