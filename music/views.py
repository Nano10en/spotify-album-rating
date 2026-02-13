from .models import Comment
from django.shortcuts import redirect, render
from .services.spotify import  get_new_releases, search_albums, get_album_details

# Create your views here.

def album_list(request):
    query = request.GET.get("q")

    if query:
        data = search_albums(query=query, limit=20)
        albums = data["albums"]["items"]
    else:
        data = get_new_releases(limit=20)
        albums = data["albums"]["items"]

    context = {
        "albums": albums,
        "query": query,
    }
    return render(request, "music/album_list.html", context)

def album_detail(request, album_id):
    album = get_album_details(album_id)
    comments = Comment.objects.filter(album_id=album_id).order_by("-created_at")
    context = {
        "album": album,
        "comments": comments,
    }
    return render(request, "music/album_detail.html", context)


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
