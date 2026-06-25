import requests
from django.conf import settings

BASE_URL = "https://www.omdbapi.com/"


def get_movie_by_imdb(imdb_id):

    params = {
        "apikey": settings.OMDB_API_KEY,
        "i": imdb_id
    }

    try:

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        if data.get("Response") == "True":
            return data

    except Exception as e:

        print(f"OMDb error for {imdb_id}: {e}")

    return None

