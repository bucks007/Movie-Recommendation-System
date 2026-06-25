from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from apps.recommender.services.personalized import (
    recommend_personalized
)


class Command(BaseCommand):

    help = "Test personalized recommendations"

    def handle(
        self,
        *args,
        **kwargs
    ):

        user = User.objects.first()

        recommendations = recommend_personalized(
            user
        )

        print(
            "\nRecommendations for:",
            user.username
        )

        for movie in recommendations:

            print(
                movie.title
            )