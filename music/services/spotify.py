import os
import base64
import requests
import secrets
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlencode

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # папка, где manage.py
load_dotenv(BASE_DIR / ".env")

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

TOKEN_URL = "https://accounts.spotify.com/api/token"
BASE_API_URL = "https://api.spotify.com/v1"
AUTH_URL = "https://accounts.spotify.com/authorize"

#Получение тоекна из Spotify API
def get_access_token():
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth_str}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

#Получение альбомов из раздела "Новые релизы"
def get_new_releases(limit=20):
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{BASE_API_URL}/browse/new-releases",
        headers=headers,
        params={"limit": limit}
    )
    response.raise_for_status()
    return response.json()

#Реализация поиска по альбомам
def search_albums(query, limit=20, offset=0):
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "q": query,
        "type": "album",
        "limit": limit,
        "offset": offset,
    }

    response = requests.get(
        f"{BASE_API_URL}/search",
        headers=headers,
        params=params
    )
    response.raise_for_status()
    return response.json()

# --- OAuth (login user) ---
def build_spotify_auth_url(session, scope="user-read-email"):
    """
    Возвращает URL, на который нужно редиректнуть пользователя.
    session — request.session (чтобы сохранить state).
    """
    state = secrets.token_urlsafe(16)
    session["spotify_oauth_state"] = state

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": scope,
        "state": state,
        "show_dialog": "true",
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def exchange_code_for_token(code):
    """
    Меняет code на access_token/refresh_token.
    """
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def get_current_user_profile(access_token):
    """
    Возвращает профиль пользователя Spotify (/v1/me).
    """
    response = requests.get(
        f"{BASE_API_URL}/me",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()