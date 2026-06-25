from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    movie_id = models.IntegerField(
        unique=True,
        null=True,
        blank=True
    )

    imdb_id = models.CharField(
        max_length=20,
        blank=True
    )
    
    tmdb_id = models.IntegerField(
        null=True,
        blank=True
    )

    title = models.CharField(
        max_length=255
    )

    overview = models.TextField()

    genres = models.CharField(
        max_length=255,
        blank=True
    )

    director = models.CharField(
        max_length=255,
        blank=True
    )

    actors = models.TextField(
        blank=True
    )

    runtime = models.CharField(
        max_length=50,
        blank=True
    )

    release_date = models.DateField(
        null=True,
        blank=True
    )

    poster_url = models.URLField(
        blank=True
    )

    backdrop_url = models.URLField(
        blank=True
    )

    vote_average = models.FloatField(
        default=0
    )

    popularity = models.FloatField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title
    
class Rating(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE
    )

    rating = models.FloatField()

    rated_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"

class Watchlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE
    )

    added_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"
