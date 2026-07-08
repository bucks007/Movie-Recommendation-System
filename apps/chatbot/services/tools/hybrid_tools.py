from langchain_core.tools import tool
from django.contrib.auth.models import User

from ..smart_recommendation_engine import smart_recommend
from ..movie_serializer import serialize_movies


@tool
def recommend_movies(query: str, user_id: int):
    """
    Recommend movies from natural language.
    """

    user = User.objects.get(id=user_id)
    movies = smart_recommend(
        user,
        query,
        top_n=10,
    )

    return {
        "message": "Recommendations",
        "movies": serialize_movies(movies),
    }