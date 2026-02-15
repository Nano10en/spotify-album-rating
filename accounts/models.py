from django.conf import settings
from django.db import models

class SpotifyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=120, unique=True)
    display_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    image = models.URLField(blank=True)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.display_name or self.spotify_id