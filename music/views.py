from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render

from .models import Comment, TrackComent
from .services.spotify import (
    get_album_details,
    get_album_tracks,
    get_new_releases,
    search_albums,
)


def _get_user_display_data(user):
    if not user.is_authenticated:
        return "", ""

    display_name = user.username
    image = ""
    try:
        profile = user.spotifyprofile
    except ObjectDoesNotExist:
        return display_name, image

    if profile.display_name:
        display_name = profile.display_name
    if profile.image:
        image = profile.image
    return display_name, image


def _resolve_author_display_name(user):
    try:
        profile = user.spotifyprofile
    except ObjectDoesNotExist:
        return user.username
    return profile.display_name or user.username


def _build_album_detail_context(request, album_id, error=""):
    album = get_album_details(album_id)
    tracks_data = get_album_tracks(album_id)

    comments = (
        Comment.objects.filter(album_id=album_id)
        .select_related("author", "author__spotifyprofile")
        .order_by("-created_at")
    )
    tracks_comments = (
        TrackComent.objects.filter(album_id=album_id)
        .select_related("author", "author__spotifyprofile")
        .order_by("-created_at")
    )

    comments_by_track = defaultdict(list)
    for track_comment in tracks_comments:
        track_comment.display_author_name = _resolve_author_display_name(track_comment.author)
        comments_by_track[track_comment.track_id].append(track_comment)

    for comment in comments:
        comment.display_author_name = _resolve_author_display_name(comment.author)

    tracks = tracks_data.get("items", [])
    for track in tracks:
        track["comments"] = comments_by_track.get(track.get("id"), [])

    auth_display_name, auth_image = _get_user_display_data(request.user)
    return {
        "album": album,
        "comments": comments,
        "tracks": tracks,
        "error": error,
        "auth_display_name": auth_display_name,
        "auth_image": auth_image,
    }

def album_list(request):
    query = request.GET.get("q")

    if query:
        data = search_albums(query=query, limit=10)
        albums = data["albums"]["items"]
    else:
        data = get_new_releases(limit=10)
        albums = data["albums"]["items"]

    auth_display_name, auth_image = _get_user_display_data(request.user)
    context = {
        "albums": albums,
        "query": query,
        "auth_display_name": auth_display_name,
        "auth_image": auth_image,
    }
    return render(request, "music/album_list.html", context)


def album_detail(request, album_id):
    context = _build_album_detail_context(request, album_id)
    return render(request, "music/album_detail.html", context)


@login_required(login_url="spotify_login")
def create_comment(request, album_id):
    if request.method == "POST":
        comment = (request.POST.get("comment") or "").strip()
        rating = request.POST.get("rating")

        if not comment:
            context = _build_album_detail_context(request, album_id, error="Comment cannot be empty.")
            return render(request, "music/album_detail.html", context)

        try:
            rating = int(rating)
        except (ValueError, TypeError):
            context = _build_album_detail_context(request, album_id, error="Rating must be an integer.")
            return render(request, "music/album_detail.html", context)

        if rating < 1 or rating > 10:
            context = _build_album_detail_context(request, album_id, error="Rating must be between 1 and 10.")
            return render(request, "music/album_detail.html", context)

        Comment.objects.create(
            author=request.user,
            album_id=album_id,
            content=comment,
            rating=rating,
        )

    return redirect("album_detail", album_id=album_id)


@login_required(login_url="spotify_login")
def create_track_comment(request, album_id, track_id):
    if request.method == "POST":
        comment = (request.POST.get("comment") or "").strip()
        rating = request.POST.get("rating")

        if not comment:
            context = _build_album_detail_context(request, album_id, error="Comment cannot be empty.")
            return render(request, "music/album_detail.html", context)

        try:
            rating = int(rating)
        except (ValueError, TypeError):
            context = _build_album_detail_context(request, album_id, error="Rating must be an integer.")
            return render(request, "music/album_detail.html", context)

        if rating < 1 or rating > 10:
            context = _build_album_detail_context(request, album_id, error="Rating must be between 1 and 10.")
            return render(request, "music/album_detail.html", context)

        TrackComent.objects.create(
            author=request.user,
            album_id=album_id,
            track_id=track_id,
            content=comment,
            rating=rating,
        )

    return redirect("album_detail", album_id=album_id)
