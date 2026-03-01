import os
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv
from django.core.cache import cache

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # папка, где manage.py
load_dotenv(BASE_DIR / ".env")

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

TOKEN_URL = "https://accounts.spotify.com/api/token"
BASE_API_URL = "https://api.spotify.com/v1"
TOKEN_CACHE_KEY = "spotify_client_access_token"

#Получение тоекна из Spotify API
def get_access_token():
    cached_token = cache.get(TOKEN_CACHE_KEY)
    if cached_token:
        return cached_token

    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth_str}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data, timeout=15)
    response.raise_for_status()
    payload = response.json()
    access_token = payload["access_token"]
    expires_in = int(payload.get("expires_in", 3600))
    cache_ttl = max(1, expires_in - 60)
    cache.set(TOKEN_CACHE_KEY, access_token, cache_ttl)
    return access_token

#Получение альбомов из раздела "Новые релизы"
def get_new_releases(limit=10):
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    limit = int(limit)
    limit = max(1, min(limit, 10))

    params = {
        "q": "tag:new",
        "type": "album",
        "market": "LV",
        "limit": limit,
    }

    response = requests.get(
        f"{BASE_API_URL}/search",
        headers=headers,
        params=params,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()

#Реализация поиска по альбомам
def search_albums(query, limit=10, offset=0):
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
        params=params,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()

def get_album_details(album_id):
    token = get_access_token()
    resp = requests.get(
        f"{BASE_API_URL}/albums/{album_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()

def get_album_tracks(album_id):
    token = get_access_token()
    resp = requests.get(
        f"{BASE_API_URL}/albums/{album_id}/tracks",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()
