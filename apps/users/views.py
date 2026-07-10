from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from apps.movies.models import Rating, Watchlist, Movie
from apps.recommender.services.personalized import recommend_personalized

from collections import Counter
import json

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(
        request,
        "users/register.html",
        {
            "form": form
        }
    )

@login_required
def profile_view(request):
    ratings = Rating.objects.filter(
        user=request.user
    ).select_related(
        "movie"
    ).order_by(
        "-rated_at"
    )
    watchlist = Watchlist.objects.filter(
        user=request.user
    ).select_related(
        "movie"
    ).order_by(
        "-added_at"
    )

    recommended_movies = recommend_personalized(
        request.user,
        top_n=8
    )
    total_ratings = ratings.count()
    watchlist_count = watchlist.count()
    
    average_rating = (
        round(
            sum(
                r.rating for r in ratings
            ) / total_ratings,
            1
        )
        if total_ratings
        else 0
    )
    rating_distribution = [0, 0, 0, 0, 0]
    genre_counter = Counter()
    for rating in ratings:
        rating_distribution[
            int(rating.rating) - 1
        ] += 1
        if rating.rating >= 4:
            genres = rating.movie.genres.split("|")
            for genre in genres:
                genre = genre.strip()
                if (
                    genre
                    and genre != "(no genres listed)"
                ):
                    genre_counter[genre] += 1
    favorite_genre = (
        max(
            genre_counter,
            key=genre_counter.get
        )
        if genre_counter
        else "N/A"
    )
    top_genres = genre_counter.most_common(5)
    rating_distribution = json.dumps(
        rating_distribution
    )
    genre_labels = json.dumps(
        [
            genre[0]
            for genre in top_genres
        ]
    )
    genre_values = json.dumps(
        [
            genre[1]
            for genre in top_genres
        ]
    )
    recent_ratings = list(
        ratings[:10]
    )
    recent_ratings.reverse()
    rating_activity_labels = json.dumps(
        [
            rating.movie.title[:18]
            for rating in recent_ratings
        ]
    )
    rating_activity_values = json.dumps(
        [
            rating.rating
            for rating in recent_ratings
        ]
    )
    dashboard_mix_labels = json.dumps(
        [
            "Ratings",
            "Watchlist",
            "Recommendations",
        ]
    )
    dashboard_mix_values = json.dumps(
        [
            total_ratings,
            watchlist_count,
            len(recommended_movies),
        ]
    )
    context = {
        "ratings": ratings,
        "watchlist": watchlist,
        "recommended_movies": recommended_movies,
        "total_ratings": total_ratings,
        "watchlist_count": watchlist_count,
        "average_rating": average_rating,
        "favorite_genre": favorite_genre,
        "rating_distribution": rating_distribution,
        "genre_labels": genre_labels,
        "genre_values": genre_values,
        "rating_activity_labels": rating_activity_labels,
        "rating_activity_values": rating_activity_values,
        "dashboard_mix_labels": dashboard_mix_labels,
        "dashboard_mix_values": dashboard_mix_values,
    }
    return render(
        request,
        "users/profile.html",
        context
    )

@login_required
def remove_watchlist_item(request,movie_id):
    movie = get_object_or_404(
        Movie,
        id=movie_id
    )
    Watchlist.objects.filter(
        user=request.user,
        movie=movie
    ).delete()
    return redirect(
        "profile"
    )

@login_required
def update_rating(request,rating_id):
    rating = get_object_or_404(
        Rating,
        id=rating_id,
        user=request.user
    )
    if request.method == "POST":
        rating.rating = float(
            request.POST.get(
                "rating"
            )
        )
        rating.save()
    return redirect("profile")
