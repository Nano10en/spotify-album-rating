from django.urls import path
from . import views

urlpatterns = [
    path("", views.album_list, name="album_list"),

    path("auth/spotify/login/", views.spotify_login, name="spotify_login"),
    path("auth/spotify/callback/", views.spotify_callback, name="spotify_callback"),
    path("auth/logout/", views.logout_view, name="logout"),
]