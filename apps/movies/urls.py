from django.urls import path
from . import views

urlpatterns = [
    path('',views.movie_list,name='movie_list'),
    path('<int:id>/',views.movie_detail,name='movie_detail'),
    path('add_to_watchlist/<int:movie_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('remove_from_watchlist/<int:movie_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('rate/<int:movie_id>/', views.rate_movie, name='rate_movie'),
]