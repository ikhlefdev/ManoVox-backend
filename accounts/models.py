from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    USERNAME_FIELD = 'email'  # This MUST be here if Djoser uses email to login
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'age']


class SignWord(models.Model):
    word = models.CharField(max_length=255)
    video_url = models.URLField(max_length=500)
    needs_ssl_bypass = models.BooleanField(default=False)
    category = models.CharField(max_length=100, default='General')

    

    def __str__(self):
        return self.word

    
    