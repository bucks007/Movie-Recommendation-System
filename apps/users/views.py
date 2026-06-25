from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from apps.movies.models import Rating, Watchlist, Movie

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
        {"form": form}
    )

@login_required
def profile_view(request):
    ratings = Rating.objects.filter(
        user=request.user
    ).select_related('movie')
    watchlist = Watchlist.objects.filter(
        user=request.user
    ).select_related('movie')

    context = {
        'ratings': ratings,
        'watchlist': watchlist,
    }
    return render(
        request,
        'users/profile.html',
        context
    )

@login_required
def remove_watchlist_item(request, movie_id):
    movie = get_object_or_404(
        Movie,
        id=movie_id
    )
    Watchlist.objects.filter(
        user=request.user,
        movie=movie
    ).delete()
    return redirect("profile")

@login_required
def update_rating(request, rating_id):

    rating = get_object_or_404(
        Rating,
        id=rating_id,
        user=request.user
    )
    if request.method == "POST":
        rating.rating = float(
            request.POST.get("rating")
        )
        rating.save()
    return redirect("profile")