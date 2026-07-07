def build_context(movies):
    context = []
    for movie in movies:
        context.append(
            f"""
            Movie Title:
            {movie.title}

            Genres:
            {movie.genres}

            Director:
            {movie.director}

            Actors:
            {movie.actors}

            Overview:
            {movie.overview}

            IMDb Rating:
            {movie.vote_average}

            Release Date:
            {movie.release_date}
            """
        )

    return "\n".join(context)