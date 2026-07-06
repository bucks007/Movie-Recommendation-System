from django.core.management.base import BaseCommand

from langchain_core.documents import Document

from apps.movies.models import Movie

from apps.chatbot.services.chroma_service import (
    get_vector_store,
)


class Command(BaseCommand):

    help = "Build Chroma Vector Database"

    def handle(self, *args, **kwargs):

        vector_store = get_vector_store()

        self.stdout.write("Loading movies...")

        movies = Movie.objects.all()

        documents = []

        ids = []

        THEME_MAP = {
            "Sci-Fi": [
                "space",
                "future",
                "technology",
                "artificial intelligence",
                "robots",
                "aliens",
                "time travel",
                "parallel universe",
                "science fiction",
                "mind bending",
                "space exploration",
                "survival",
            ],

            "Drama": [
                "emotional",
                "relationships",
                "family",
                "character driven",
                "life",
                "human emotions",
                "heartwarming",
            ],

            "Romance": [
                "love",
                "romantic",
                "relationship",
                "heartwarming",
                "emotional",
            ],

            "Adventure": [
                "journey",
                "exploration",
                "quest",
                "survival",
                "discovery",
            ],

            "Thriller": [
                "suspense",
                "mystery",
                "crime",
                "psychological",
                "tension",
            ],

            "Crime": [
                "detective",
                "investigation",
                "gangsters",
                "mafia",
                "police",
            ],

            "Fantasy": [
                "magic",
                "mythical",
                "dragons",
                "imaginary world",
            ],

            "Comedy": [
                "funny",
                "humor",
                "lighthearted",
                "feel good",
            ],

            "Horror": [
                "fear",
                "ghost",
                "supernatural",
                "monster",
                "scary",
            ],
        }

        for movie in movies:
            if not movie.overview or len(movie.overview.strip()) < 30:
                continue

            themes = []

            for genre in (movie.genres or "").split(","):

                genre = genre.strip()

                themes.extend(
                    THEME_MAP.get(
                        genre,
                        []
                    )
                )

            themes = ", ".join(sorted(set(themes)))

            text = f"""
                Movie Title:
                {movie.title}

                Also Known As:
                {movie.title}

                Overview:
                {movie.overview}

                Genres:
                {movie.genres}

                Themes:
                {themes}

                Director:
                {movie.director}

                Actors:
                {movie.actors}

                Release Year:
                {movie.release_date.year if movie.release_date else "Unknown"}

                IMDb Rating:
                {movie.vote_average}

                This movie is suitable for viewers interested in:
                {themes}

                People may search for this movie using:
                - {movie.title}
                - {movie.director}
                - {movie.actors}
                - {movie.genres}
                """

            doc = Document(
                page_content=text,
                metadata={
                    "movie_id": movie.movie_id,
                    "title": movie.title,
                    "genres": movie.genres,
                    "director": movie.director,
                    "year": (
                        movie.release_date.year
                        if movie.release_date
                        else None
                    ),
                    "vote_average": movie.vote_average,
                },
            )

            documents.append(doc)

            ids.append(str(movie.movie_id))

        BATCH_SIZE = 250

        total = len(documents)

        for start in range(0, total, BATCH_SIZE):

            end = min(start + BATCH_SIZE, total)

            self.stdout.write(
                f"Embedding movies {start+1} - {end} of {total}"
            )

            vector_store.add_documents(
                documents=documents[start:end],
                ids=ids[start:end],
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Vector DB created successfully."
            )
        )
    