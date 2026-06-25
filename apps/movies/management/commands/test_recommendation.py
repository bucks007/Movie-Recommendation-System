from django.core.management.base import BaseCommand

from apps.recommender.services.content_based import (
    recommend_movies
)


class Command(BaseCommand):

    help = "Test recommendation system"

    def handle(self, *args, **kwargs):

        movie = "Toy Story (1995)"

        recommendations = recommend_movies(
            movie
        )

        self.stdout.write(
            f"\nRecommendations for: {movie}\n"
        )

        for rec in recommendations:
            self.stdout.write(rec)