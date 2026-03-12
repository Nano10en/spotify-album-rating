from collections import defaultdict
from django.contrib import messages
from django.http import JsonResponse

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


def _build_album_detail_context(request, album_id):
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
        "auth_display_name": auth_display_name,
        "auth_image": auth_image,
    }

def rated_albums():
    album_ids = (
        Comment.objects
        .order_by("-created_at")
        .values_list("album_id", flat=True)
        .distinct()
    )[:10]

    rated_albums = []
    for album_id in album_ids:
        rated_albums.append(get_album_details(album_id))

    return rated_albums

def ajax_album_search(request):
    query = request.GET.get("q")

    if not query:
        return JsonResponse({"albums": []})
    
    data = search_albums(query=query, limit=10)
    items = data.get("albums", {}).get("items", [])

    albums = []
    for album in items:
        images = album.get("images", [])
        artists = album.get("artists", [])

        albums.append({
            "id": album.get("id"),
            "name": album.get("name"),
            "artist": ", ".join(artist.get("name", "") for artist in artists),
            "image": images[0]["url"] if images else "",
            "url": f"/album/{album.get('id')}/"
        })
    
    return JsonResponse({"albums": albums})

def album_list(request):
    rated_albums_list = rated_albums()

    new_releases = get_new_releases(limit=10)
    new_releases_albums = new_releases["albums"]["items"]

    auth_display_name, auth_image = _get_user_display_data(request.user)
    context = {
        "new_releases": new_releases_albums,
        "auth_display_name": auth_display_name,
        "auth_image": auth_image,
        "rated_albums": rated_albums_list
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
            messages.error(request, "Comment cannot be empty.")
            return redirect("album_detail", album_id=album_id)

        try:
            rating = int(rating)
        except (ValueError, TypeError):
            messages.error(request, "Rating must be an integer.")
            return redirect("album_detail", album_id=album_id)

        if rating < 1 or rating > 10:
            messages.error(request, "Rating must be between 1 and 10.")
            return redirect("album_detail", album_id=album_id)
        
        if Comment.objects.filter(author=request.user, album_id=album_id).exists():
            messages.error(request, "You have already left a comment for this album.")
            return redirect("album_detail", album_id=album_id)

        Comment.objects.create(
            author=request.user,
            album_id=album_id,
            content=comment,
            rating=rating,
        )

        messages.success(request, "Comment added successfully.")

    return redirect("album_detail", album_id=album_id)


@login_required(login_url="spotify_login")
def create_track_comment(request, album_id, track_id):
    if request.method == "POST":
        comment = (request.POST.get("comment") or "").strip()
        rating = request.POST.get("rating")

        if not comment:
            messages.error(request, "Comment cannot be empty.")
            return redirect("album_detail", album_id=album_id)

        try:
            rating = int(rating)
        except (ValueError, TypeError):
            messages.error(request, "Rating must be an integer.")
            return redirect("album_detail", album_id=album_id)

        if rating < 1 or rating > 10:
            messages.error(request, "Rating must be between 1 and 10.")
            return redirect("album_detail", album_id=album_id)
        
        if TrackComent.objects.filter(author=request.user, track_id=track_id, album_id=album_id).exists():
            messages.error(request, "You have already left a comment for this track.")
            return redirect("album_detail", album_id=album_id)

        TrackComent.objects.create(
            author=request.user,
            album_id=album_id,
            track_id=track_id,
            content=comment,
            rating=rating,
        )

        messages.success(request, "Comment added successfully.")

    return redirect("album_detail", album_id=album_id)