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

        for movie in movies:

            text = f"""
                Movie Title:
                {movie.title}

                Genres:
                {movie.genres}

                Director:
                {movie.director}

                Actors:
                {movie.actors}

                Movie Story:
                {movie.overview}

                This movie belongs to these genres:
                {movie.genres}

                Main cast:
                {movie.actors}

                Directed by:
                {movie.director}

                Release Year:
                {movie.release_date.year if movie.release_date else "Unknown"}

                IMDb Rating:
                {movie.vote_average}

                This document describes the movie "{movie.title}".
                It can answer questions about:
                - story
                - plot
                - actors
                - cast
                - director
                - genre
                - science fiction
                - romance
                - comedy
                - horror
                - thriller
                - adventure
                - animation
                - action
                - family
                - mystery
                - fantasy
                """

            doc = Document(
                page_content=text,
                metadata={
                    "movie_id": movie.movie_id,
                    "title": movie.title,
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
    