from apps.movies.models import Rating
from apps.recommender.services.hybrid import recommend_hybrid


def recommend_personalized(
    user,
    top_n=10
):
    """
    Personalized recommendations based on
    the user's highest-rated movies.
    """

    ratings = (
        Rating.objects
        .filter(
            user=user
        )
        .order_by(
            "-rating"
        )[:5]
    )

    if not ratings:
        return []

    recommended_movies = []
    added_ids = set()

    for rating in ratings:

        movie = rating.movie

        recommendations = recommend_hybrid(
            movie.title,
            top_n=5
        )

        for rec in recommendations:

            # don't recommend movies already rated
            if Rating.objects.filter(
                user=user,
                movie=rec
            ).exists():
                continue

            if rec.id not in added_ids:

                recommended_movies.append(
                    rec
                )

                added_ids.add(
                    rec.id
                )

        if len(recommended_movies) >= top_n:
            break

    return recommended_movies[:top_n]