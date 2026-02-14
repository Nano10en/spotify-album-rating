from django.urls import path
from . import views

urlpatterns = [
    path("", views.album_list, name="album_list"),
    path("album/<str:album_id>/", views.album_detail, name="album_detail"),
    path("album/<str:album_id>/comment/", views.create_comment, name="create_comment"),
    path("album/<str:album_id>/comment/track/<str:track_id>/", views.create_track_comment, name="create_track_comment"),
]