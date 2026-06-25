import pandas as pd
import joblib
import os

from sklearn.neighbors import NearestNeighbors


def train_collaborative_model():

    print("Loading ratings dataset...")

    ratings = pd.read_csv(
        "datasets/ml-latest-small/ratings.csv"
    )

    print(f"Loaded {len(ratings)} ratings")

    print("Creating User-Movie Matrix...")

    user_movie_matrix = ratings.pivot_table(
        index="movieId",
        columns="userId",
        values="rating"
    ).fillna(0)

    print(
        f"Matrix Shape: {user_movie_matrix.shape}"
    )

    print("Training Collaborative Model...")

    model = NearestNeighbors(
        metric="cosine",
        algorithm="brute",
        n_neighbors=20
    )

    model.fit(user_movie_matrix)

    os.makedirs(
        "ml_models",
        exist_ok=True
    )

    print("Saving model files...")

    joblib.dump(
        model,
        "ml_models/collaborative_model.joblib"
    )

    joblib.dump(
        user_movie_matrix,
        "ml_models/user_movie_matrix.joblib"
    )

    print(
        "Collaborative Filtering Model Trained Successfully!"
    )


if __name__ == "__main__":
    train_collaborative_model()