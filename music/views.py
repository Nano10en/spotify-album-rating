from django.shortcuts import render
from .services.spotify import  get_new_releases, search_albums

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
