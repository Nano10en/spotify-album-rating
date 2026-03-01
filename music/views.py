from .models import Comment, TrackComent
from django.shortcuts import redirect, render
from .services.spotify import (
    get_album_tracks, 
    get_new_releases, 
    search_albums, 
    get_album_details
)
from django.contrib.auth.decorators import login_required

# Dictionary for track comments, where key is track_id and value is a list of comments for that track
from collections import defaultdict

# Create your views here.

def album_list(request):
    query = request.GET.get("q")

    if query:
        data = search_albums(query=query, limit=10)
        albums = data["albums"]["items"]
    else:
        data = get_new_releases(limit=10)
        albums = data["albums"]["items"]

    context = {
        "albums": albums,
        "query": query,
    }
    return render(request, "music/album_list.html", context)

def album_detail(request, album_id):
    album = get_album_details(album_id)
    tracks_data = get_album_tracks(album_id)

    comments = Comment.objects.filter(album_id=album_id).order_by("-created_at")
    tracks_comments = TrackComent.objects.filter(album_id=album_id).order_by("-created_at")

    comments_by_track = defaultdict(list)
    for c in tracks_comments:
        comments_by_track[c.track_id].append(c)

    tracks = tracks_data["items"]    

    for t in tracks:
        tid = t.get("id")  # spotify track id
        t["comments"] = comments_by_track.get(tid, [])

    context = {
        "album": album,
        "comments": comments,
        "tracks": tracks,
    }
    return render(request, "music/album_detail.html", context)

@login_required(login_url="spotify_login")
def create_comment(request, album_id):
    album = get_album_details(album_id)

    if request.method == "POST":
        comment = (request.POST.get("comment")).strip()
        rating = request.POST.get("rating")

        if not comment:
            return render(request, "music/album_detail.html", 
                {"album": album, "error": "Comment cannot be empty."}
            )
        
        try:
            rating = int(rating)
        except (ValueError, TypeError):
            return render(request, "music/album_detail.html", 
                {"album": album, "error": "Rating must be an integer."}
            )
        
        if rating < 1 or rating > 10:
            return render(request, "music/album_detail.html", 
                {"album": album, "error": "Rating must be between 1 and 10."}
            )
    
        Comment.objects.create(
            author=request.user,
            album_id=album_id,
            content=comment,
            rating=rating,
        )

    return redirect("album_detail", album_id=album_id)

def create_track_comment(request, album_id, track_id):
    album = get_album_details(album_id)

    if request.method == "POST":
        comment = (request.POST.get("comment")).strip()
        rating = request.POST.get("rating")

        if not comment:
            return render(request, "music/album_detail.html", 
                {"album": album, "error": "Comment cannot be empty."}
            )
        
        try:
            rating = int(rating)
        except (ValueError, TypeError):
            return render(request, "music/album_detail.html", 
                {"album": album, "error": "Rating must be an integer."}
            )
        
        if rating < 1 or rating > 10:
            return render(request, "music/album_detail.html", 
                {"album": album, "error": "Rating must be between 1 and 10."}
            )
    
        TrackComent.objects.create(
            author=request.user,
            album_id=album_id,
            track_id=track_id,
            content=comment,
            rating=rating,
        )

    return redirect("album_detail", album_id=album_id)