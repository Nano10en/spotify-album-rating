# Spotyfy Album Rating
## This project was made with Spotify API

## Setup

### 1) Install
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt

### 2) Env
copy .env.example .env
# fill SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, SECRET_KEY
You can get keys from Spotify Developer Dashboard

### 3) Run
python manage.py migrate
python manage.py runserver