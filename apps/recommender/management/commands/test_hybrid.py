from django.core.management.base import BaseCommand

from apps.recommender.services.hybrid import recommend_hybrid


class Command(BaseCommand):

    help = "Test Hybrid Recommendation"

    def handle(self, *args, **kwargs):

        movie_title = "Toy Story (1995)"

        recommendations = recommend_hybrid(
            movie_title,
            top_n=10
        )

        self.stdout.write(
            f"\nRecommendations for: {movie_title}\n"
        )

        for movie in recommendations:

            self.stdout.write(
                movie.title
            )