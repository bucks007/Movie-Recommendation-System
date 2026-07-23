import re
from rapidfuzz import process, fuzz
from apps.movies.models import Movie
from .memory_store import get_state
from .conversation_memory import remember_movie


class MovieParser:

    @staticmethod
    def clean_query(message):

        query = re.sub(
            r"\b("
            r"who|what|when|where|tell|me|about|"
            r"director|directed|actor|actors|cast|"
            r"this|that|it|its|"
            r"plot|story|runtime|release|released|"
            r"rating|imdb|movie|movies|film|"
            r"similar|like|recommend|recommended|"
            r"recommendation|suggest|show|find|search|"
            r"to|for|of|is|the"
            r")\b",
            "",
            message,
            flags=re.IGNORECASE,
        )

        return re.sub(r"\s+", " ", query).strip()

    @staticmethod
    def find_movie(user,message):
        query = MovieParser.clean_query(message)

        msg = message.lower()

        # If the user refers to the previous movie, return it immediately
        if any(
            word in msg
            for word in [
                "this",
                "that",
                "it",
                "its",
            ]
        ):
            movie = MovieParser.get_last_movie(user)
            if movie:
                return movie

        # Remove punctuation after cleaning
        query = re.sub(r"[^\w\s]", "", query).strip()

        # Avoid fuzzy searching empty queries like "?"
        if len(query) < 3:
            return None

        if not query:
            return None

    # -------------------------
    # 1 Exact Match
    # -------------------------

        movie = Movie.objects.filter(
            title__iexact=query
        ).first()

        if movie:
            remember_movie(user, movie)
            return movie

    # -------------------------
    # 2 Partial Match
    # -------------------------

        movies = Movie.objects.filter(
            title__icontains=query
        )

        if movies.exists():
            movie = movies.order_by(
                "-vote_average",
                "-release_date"
            ).first()
            remember_movie(user, movie)
            return movie


        # -------------------------
        # 3 RapidFuzz
        # -------------------------

        movies = list(
            Movie.objects.only(
                "id",
                "title"
            )
        )

        titles = [
            m.title
            for m in movies
        ]

        match = process.extractOne(
            query,
            titles,
            scorer=fuzz.WRatio
        )

        if not match:
            return None

        title, score, _ = match

        if score < 80:
            return None

        for movie in movies:

            if movie.title == title:
                movie = Movie.objects.get(
                    id=movie.id
                )
                remember_movie(user, movie)
                return movie

        return None
    
    @staticmethod
    def get_last_movie(user):

        state = get_state(user.id)

        movie_id= state.get("last_movie_id")

        if not movie_id:
            return None

        return Movie.objects.filter(
            id=movie_id
        ).first()