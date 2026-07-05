def serialize_movies(movies):

    data = []

    for movie in movies:

        data.append({

            "id": movie.id,

            "movie_id": movie.movie_id,

            "title": movie.title,

            "poster": (
                movie.poster_url
                if movie.poster_url
                else "https://placehold.co/300x450?text=No+Poster"
            ),

            "rating": movie.vote_average,

            "genres": movie.genres,

            "year": (
                movie.release_date.year
                if movie.release_date
                else None
            ),

        })

    return data