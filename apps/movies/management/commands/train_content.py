from django.core.management.base import BaseCommand
from apps.movies.models import Movie

import pandas as pd
import joblib
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Command(BaseCommand):
    help = "Train content-based recommendation model"

    def handle(self, *args, **kwargs):

        self.stdout.write("Fetching movies from database...")

        movies = Movie.objects.all().values(
            "movie_id",
            "title",
            "genres"
        )

        df = pd.DataFrame(list(movies))

        if df.empty:
            self.stdout.write(
                self.style.ERROR("No movies found.")
            )
            return

        self.stdout.write(
            f"Found {len(df)} movies"
        )

        df["genres"] = df["genres"].fillna("")

        df["genres"] = df["genres"].apply(
            lambda x: x.replace("|", " ")
        )

        self.stdout.write(
            "Creating TF-IDF vectors..."
        )

        tfidf = TfidfVectorizer(
            stop_words="english"
        )

        tfidf_matrix = tfidf.fit_transform(
            df["genres"]
        )

        self.stdout.write(
            "Calculating cosine similarity..."
        )

        cosine_sim = cosine_similarity(
            tfidf_matrix,
            tfidf_matrix
        )

        indices = pd.Series(
            df.index,
            index=df["title"]
        ).drop_duplicates()

        os.makedirs(
            "ml_models",
            exist_ok=True
        )

        joblib.dump(
            tfidf,
            "ml_models/tfidf.joblib"
        )

        joblib.dump(
            cosine_sim,
            "ml_models/cosine_similarity.joblib"
        )

        joblib.dump(
            indices,
            "ml_models/movie_indices.joblib"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Model trained successfully!"
            )
        )