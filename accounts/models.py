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

class ASLLetter(models.Model):
    letter = models.CharField(max_length=1, unique=True)
    image = models.ImageField(upload_to='asl_images/', null=True, blank=True)
    video = models.FileField(upload_to='asl_videos/', null=True, blank=True)

    def __str__(self):
        return f"Letter: {self.letter.upper()}"
    