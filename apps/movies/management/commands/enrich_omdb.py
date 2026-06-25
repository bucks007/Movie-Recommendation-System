from django.core.management.base import BaseCommand
from apps.movies.models import Movie
from apps.movies.services.omdb_service import get_movie_by_imdb

from datetime import datetime
import time

class Command(BaseCommand):
    help = "Enrich movies using OMDb API"
    def handle(self, *args, **kwargs):
        movies = Movie.objects.filter(
            poster_url=""
        )[:500]
        total = movies.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Found {total} movies to enrich"
            )
        )
        for index, movie in enumerate(movies, start=1):
            if not movie.imdb_id:
                continue
            
            self.stdout.write(
                f"[{index}/{total}] {movie.title}"
            )

            try:
                data = get_movie_by_imdb(movie.imdb_id)

                if not data:
                    continue
            except Exception as e:
                print(f"Failed: {movie.title}")
                print(e)
                continue

            movie.overview = data.get(
                "Plot",
                movie.overview
            )

            movie.poster_url = data.get(
                "Poster",
                ""
            )

            movie.genres = data.get(
                "Genre",
                movie.genres
            )

            movie.director = data.get(
                "Director",
                ""
            )

            movie.actors = data.get(
                "Actors",
                ""
            )

            movie.runtime = data.get(
                "Runtime",
                ""
            )

            movie.imdb_id = data.get(
                "imdbID",
                ""
            )
            try:
                movie.vote_average = float(
                    data.get(
                        "imdbRating",
                        0
                    )
                )
            except:
                pass
            released = data.get(
                "Released"
            )
            if released and released != "N/A":
                try:
                    movie.release_date = datetime.strptime(
                        released,
                        "%d %b %Y"
                    ).date()
                except:
                    pass
            movie.save()
            time.sleep(0.2)

        self.stdout.write(
            self.style.SUCCESS(
                "OMDb enrichment completed!"
            )
        )