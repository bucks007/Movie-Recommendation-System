from django.core.management.base import BaseCommand

from apps.movies.models import Movie
from apps.recommender.services.collaborative import (
    recommend_collaborative
)


class Command(BaseCommand):

    help = "Test Collaborative Recommendations"

    def handle(self, *args, **kwargs):

        movie = Movie.objects.get(
            movie_id=1
        )

        recommendations = (
            recommend_collaborative(
                movie.movie_id
            )
        )

        print(
            f"\nRecommendations for: {movie.title}\n"
        )

        for rec in recommendations:

            print(rec.title)