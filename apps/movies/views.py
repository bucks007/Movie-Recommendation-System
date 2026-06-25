from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .models import Movie, Watchlist, Rating
from apps.recommender.services.hybrid import recommend_hybrid
from apps.recommender.services.personalized import recommend_personalized

def movie_list(request):

    query = request.GET.get("q", "")
    movies = Movie.objects.all().order_by("title")
    if query:
        movies = movies.filter(
            Q(title__icontains=query)
        )

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

    context = {
        "page_obj": page_obj,
        "query": query,
        "personalized_movies": personalized_movies
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
        movie.title,
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