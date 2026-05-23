from django.db import models
from django.conf import settings # <-- Add this import

class TranslationHistory(models.Model):
    # Change 'User' to 'settings.AUTH_USER_MODEL'
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    
    original_text = models.TextField()
    video_url = models.URLField(max_length=500)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.original_text[:20]}..."