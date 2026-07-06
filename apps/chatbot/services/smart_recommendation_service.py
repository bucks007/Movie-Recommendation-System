import re

from django.db.models import Q

from apps.movies.models import Movie


GENRES = [
    "Action",
    "Adventure",
    "Animation",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Fantasy",
    "Horror",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Thriller",
    "War",
    "Western",
]


MOODS = {
    "emotional": [
        "emotion",
        "love",
        "family",
        "loss",
        "hope",
        "relationship",
        "heart",
        "grief",
        "life",
    ],

    "dark": [
        "dark",
        "crime",
        "killer",
        "revenge",
        "murder",
        "violence",
    ],

    "mind bending": [
        "dream",
        "memory",
        "parallel",
        "reality",
        "time",
        "dimension",
        "consciousness",
    ],

    "feel good": [
        "friendship",
        "hope",
        "happy",
        "journey",
        "kindness",
    ],

    "inspirational": [
        "dream",
        "success",
        "achievement",
        "courage",
        "perseverance",
    ],
}


def recommend_by_query(query, limit=12):

    text = query.lower()

    genre = None

    for g in GENRES:
        if g.lower() in text:
            genre = g
            break

    mood = None

    for m in MOODS:
        if m in text:
            mood = m
            break

    movies = Movie.objects.all()

    if genre:
        movies = movies.filter(
            genres__icontains=genre
        )

    results = []

    for movie in movies:

        score = 0

        overview = (movie.overview or "").lower()

        if mood:

            for keyword in MOODS[mood]:

                if keyword in overview:
                    score += 1

        results.append(
            (
                score,
                movie.vote_average or 0,
                movie,
            )
        )

    results.sort(
        key=lambda x: (
            x[0],
            x[1],
        ),
        reverse=True,
    )

    return [
        x[2]
        for x in results[:limit]
    ]