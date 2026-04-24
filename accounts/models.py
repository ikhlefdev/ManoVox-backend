import random

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from cloudinary_storage.storage import VideoMediaCloudinaryStorage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    age = models.PositiveIntegerField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=[('user', 'User'), ('admin', 'Administration')], default='user')
    organization_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    USERNAME_FIELD = 'email'  # This MUST be here if Djoser uses email to login
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'age', 'role']


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
    video = models.FileField(upload_to='asl_videos/', null=True, blank=True, storage=VideoMediaCloudinaryStorage())

    def __str__(self):
        return f"Letter: {self.letter.upper()}"
    
    

class PasswordResetCode(models.Model):
    # This creates a relationship. If a User is deleted, their reset codes are also deleted automatically (CASCADE).
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # The actual 6-digit code. We save it as a string (CharField) because passwords/codes shouldn't be treated as math numbers.
    code = models.CharField(max_length=6)
    
    # Automatically records the exact time this code was generated. You could use this later to make codes "expire" after 15 minutes
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        # Pick a random number between 100,000 and 999,999. Convert it into a string. Then assign it to this record's 'code' field.
        self.code = str(random.randint(100000, 999999))
        
        # Save this new code into the PostgreSQL database.
        self.save()
        
class EmailVerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def generate_code(self):
        # Generates a random 6-digit string
        from django.utils.crypto import get_random_string
        self.code = get_random_string(length=6, allowed_chars='0123456789')
        self.save()
        
