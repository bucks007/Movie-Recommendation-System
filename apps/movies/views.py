from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from urllib.parse import urlencode
import re
from .models import Movie, Watchlist, Rating
from apps.recommender.services.hybrid import recommend_hybrid
from apps.recommender.services.personalized import recommend_personalized

def split_genres(genre_string):
    """Normalize genres stored with either comma or pipe separators."""
    return [
        genre.strip()
        for genre in re.split(r"[|,]", genre_string or "")
        if genre.strip() and genre.strip() != "(no genres listed)"
    ]


def movie_list(request):

    query = request.GET.get("q", "").strip()
    selected_genres = list(dict.fromkeys(
        genre.strip() for genre in request.GET.getlist("genre") if genre.strip()
    ))
    selected_rating = request.GET.get("rating", "").strip()
    selected_year = request.GET.get("year", "").strip()
    movies = Movie.objects.all().order_by("title")
    if query:
        movies = movies.filter(
            Q(title__icontains=query)
        )

    if selected_genres:
        genre_filter = Q()
        for genre in selected_genres:
            genre_filter |= Q(genres__icontains=genre)
        movies = movies.filter(genre_filter)

    try:
        if selected_rating:
            movies = movies.filter(vote_average__gte=float(selected_rating))
    except ValueError:
        selected_rating = ""

    try:
        if selected_year:
            movies = movies.filter(release_date__year=int(selected_year))
    except ValueError:
        selected_year = ""

    paginator = Paginator(
        movies,
        20
    )  # 20 movies per page

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    personalized_movies = []

    if request.user.is_authenticated:
        personalized_movies = recommend_personalized(
            request.user,
            top_n=8
        )

    genre_options = sorted({
        genre
        for genre_list in Movie.objects.exclude(genres="").values_list("genres", flat=True)
        for genre in split_genres(genre_list)
    })
    year_options = Movie.objects.exclude(
        release_date__isnull=True
    ).dates("release_date", "year", order="DESC")
    filter_params = [("genre", genre) for genre in selected_genres]
    filter_params.extend((key, value) for key, value in {
        "q": query,
        "rating": selected_rating,
        "year": selected_year,
    }.items() if value)
    filter_query = urlencode(filter_params, doseq=True)

    context = {
        "page_obj": page_obj,
        "query": query,
        "personalized_movies": personalized_movies,
        "page_numbers": paginator.get_elided_page_range(number=page_obj.number, on_each_side=1, on_ends=1),
        "genre_options": genre_options,
        "year_options": year_options,
        "selected_genres": selected_genres,
        "selected_rating": selected_rating,
        "selected_year": selected_year,
        "filter_query": filter_query,
    }

    return render(
        request,
        "movies/movie_list.html",
        context
    )

def movie_detail(request, id):

    movie = get_object_or_404(
        Movie,
        id=id
    )

    recommendations = recommend_hybrid(
        movie.movie_id,
        top_n=10
    )

    is_in_watchlist = False
    user_rating = None

    if request.user.is_authenticated:

        is_in_watchlist = Watchlist.objects.filter(
            user=request.user,
            movie=movie
        ).exists()

        rating = Rating.objects.filter(
            user=request.user,
            movie=movie
        ).first()

        if rating:
            user_rating = rating.rating

    top_rated_movies = Movie.objects.exclude(
        vote_average=0
    ).order_by(
        "-vote_average"
    )[:8]

    recent_movies = Movie.objects.order_by(
        "-created_at"
    )[:8]

    context = {
        "movie": movie,
        "recommendations": recommendations,
        "is_in_watchlist": is_in_watchlist, 
        "user_rating": user_rating,
        "top_rated_movies": top_rated_movies,
        "recent_movies": recent_movies
    }
    
    return render(
        request,
        "movies/movie_detail.html",
        context
    )
@login_required
def add_to_watchlist(request, movie_id):

    if request.method == "POST":

        movie = get_object_or_404(
            Movie,
            id=movie_id
        )

        Watchlist.objects.get_or_create(
            user=request.user,
            movie=movie
        )

    return redirect(
        "movie_detail",
        id=movie_id
    )

@login_required
def remove_from_watchlist(request, movie_id):

    movie = get_object_or_404(
        Movie,
        id=movie_id
    )

    Watchlist.objects.filter(
        user=request.user,
        movie=movie
    ).delete()

    return redirect(
        "movie_detail",
        id=movie.id
    )

@login_required
def rate_movie(request, movie_id):

    movie = get_object_or_404(
        Movie,
        id=movie_id
    )

    if request.method == "POST":

        rating_value = float(
            request.POST.get("rating")
        )

        Rating.objects.update_or_create(

            user=request.user,

            movie=movie,

            defaults={
                "rating": rating_value
            }

        )

    return redirect(
        "movie_detail",
        id=movie.id
    )
