from django.db import models
from django.contrib.auth.models import User

class Comment(models.Model):
    author = models.ForeignKey(User, verbose_name='Author name', on_delete=models.DO_NOTHING)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.IntegerField(default=0)
    album_id = models.CharField(max_length=120)

    def __str__(self):
        return f"Comment by {self.author} at {self.created_at}"
 