# Spotify Album Rating (Django + Spotify API)

Web app that connects to Spotify and lets users browse albums and leave ratings/reviews.
Focus: OAuth, API integration, backend logic, and clean UI templates.

## Features
- Spotify OAuth (login + token handling)
- Search albums / view album details (tracks, artists, release info)
- Ratings & reviews (stored in DB)
- User accounts and profile basics

## Tech stack
- Python, Django
- SQLite/PostgreSQL (depending on setup)
- HTML templates + CSS
- Spotify Web API

## Screenshots
- `docs/album_list.png`
- `docs/album_details.png`

## Getting started (local)
### Requirements
- Python 3.10+
- Spotify Developer account (Client ID/Secret)

### Setup
```bash
git clone https://github.com/Nano10en/spotify-album-rating.git
cd spotify-album-rating

python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver