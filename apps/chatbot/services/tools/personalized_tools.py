from langchain_core.tools import tool

from apps.recommender.services.personalized import (
    recommend_personalized,
)
from ..movie_serializer import serialize_movies
from django.contrib.auth.models import User


@tool
def personalized_recommendations(user_id: int):
    """
    Recommend movies based on the user's ratings.
    """

    user = User.objects.get(id=user_id)
    movies = recommend_personalized(user)

    return {
        "message": "Personalized recommendations",
        "movies": serialize_movies(movies),
    }