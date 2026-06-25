from django.core.management.base import BaseCommand

from apps.recommender.training.train_collaborative import (
    train_collaborative_model
)


class Command(BaseCommand):

    help = "Train Collaborative Recommendation Model"

    def handle(self, *args, **kwargs):

        train_collaborative_model()