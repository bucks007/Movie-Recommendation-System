from django.core.management.base import BaseCommand
from apps.movies.models import Movie
import csv
import os


class Command(BaseCommand):
    help = "Import movies from MovieLens dataset"

    def handle(self, *args, **kwargs):

        movies_path = os.path.join(
            "datasets",
            "ml-latest-small",
            "movies.csv"
        )

        links_path = os.path.join(
            "datasets",
            "ml-latest-small",
            "links.csv"
        )

        links = {}

        with open(links_path, encoding="utf-8") as file:

            reader = csv.DictReader(file)

            for row in reader:

                links[row["movieId"]] = {
                    "imdb_id": row["imdbId"],
                    "tmdb_id": row["tmdbId"]
                }

        count = 0

        with open(movies_path, encoding="utf-8") as file:

            reader = csv.DictReader(file)

            for row in reader:

                movie_id = row["movieId"]

                imdb_id = ""
                tmdb_id = None

                if movie_id in links:

                    if links[movie_id]["imdb_id"]:

                        imdb_id = (
                            f"tt{int(links[movie_id]['imdb_id']):07d}"
                        )

                    if links[movie_id]["tmdb_id"]:

                        tmdb_id = int(
                            float(
                                links[movie_id]["tmdb_id"]
                            )
                        )

                Movie.objects.update_or_create(

                    movie_id=movie_id,

                    defaults={
                        "title": row["title"],
                        "genres": row["genres"],
                        "imdb_id": imdb_id,
                        "tmdb_id": tmdb_id,
                    }
                )

                count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {count} movies."
            )
        )