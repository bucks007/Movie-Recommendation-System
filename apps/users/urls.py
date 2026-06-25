from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register_view, profile_view, remove_watchlist_item, update_rating

urlpatterns = [

    path("register/",register_view,name="register"),
    path("login/",auth_views.LoginView.as_view(template_name="users/login.html"),name="login"),
    path("logout/",auth_views.LogoutView.as_view(),name="logout"),
    path("profile/",profile_view,name="profile"),
    path("remove-watchlist/<int:movie_id>/", remove_watchlist_item, name="remove_watchlist_item"),
    path("update-rating/<int:rating_id>/", update_rating, name="update_rating"),
]