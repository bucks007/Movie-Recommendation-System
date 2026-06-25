from apps.movies.models import Movie
import pandas as pd
import joblib
import os
import django

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Setup Django Environment
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()


def train_content_model():

    print("Fetching movies from database...")

    movies = Movie.objects.all().values(
        "movie_id",
        "title",
        "genres"
    )

    df = pd.DataFrame(list(movies))

    if df.empty:
        print("No movies found in database.")
        return

    print(f"Found {len(df)} movies")

    # Replace NaN values
    df["genres"] = df["genres"].fillna("")

    # Convert:
    # Action|Adventure|Sci-Fi
    # ->
    # Action Adventure Sci-Fi

    df["genres"] = df["genres"].apply(
        lambda x: x.replace("|", " ")
    )

    print("Creating TF-IDF vectors...")

    tfidf = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = tfidf.fit_transform(
        df["genres"]
    )

    print("Calculating cosine similarity...")

    cosine_sim = cosine_similarity(
        tfidf_matrix,
        tfidf_matrix
    )

    # Create title -> dataframe index mapping

    indices = pd.Series(
        df.index,
        index=df["title"]
    ).drop_duplicates()

    os.makedirs(
        "ml_models",
        exist_ok=True
    )

    print("Saving model files...")

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

    print("Content-Based Recommendation Model Trained Successfully!")


if __name__ == "__main__":
    train_content_model()