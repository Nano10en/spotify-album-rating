from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from .models import SpotifyProfile

from .services.spotify_oauth import (
    build_spotify_auth_url,
    exchange_code_for_token,
    get_current_user_profile,
)

# Create your views here.

def spotify_login(request):
    url = build_spotify_auth_url(request.session, scope="user-read-email")
    return redirect(url)


def spotify_callback(request):
    error = request.GET.get("error")
    if error:
        return redirect("album_list")

    state = request.GET.get("state")
    saved_state = request.session.get("spotify_oauth_state")
    if not saved_state or state != saved_state:
        return redirect("album_list")

    code = request.GET.get("code")
    if not code:
        return redirect("album_list")

    token_data = exchange_code_for_token(code)
    access_token = token_data.get("access_token", "")
    refresh_token = token_data.get("refresh_token", "")
    expires_in = int(token_data.get("expires_in", 0))

    me = get_current_user_profile(access_token)

    spotify_id = me["id"]
    display_name = me.get("display_name") or ""
    email = me.get("email") or ""
    image = me.get("images", [{}])[0].get("url", "")

    user, _ = User.objects.get_or_create(
        username=f"spotify_{spotify_id}",
        defaults={"email": email},
    )

    expires_at = timezone.now() + timezone.timedelta(seconds=expires_in) if expires_in else None

    profile, _ = SpotifyProfile.objects.get_or_create(
        user=user,
        defaults={"spotify_id": spotify_id},
    )
    profile.spotify_id = spotify_id
    profile.display_name = display_name
    profile.email = email
    profile.image = image
    profile.access_token = access_token
    if refresh_token:
        profile.refresh_token = refresh_token
    profile.token_expires_at = expires_at
    profile.save()

    login(request, user)
    return redirect("album_list")


def logout_view(request):
    logout(request)
    return redirect("album_list")
