from django.db import models
from accounts.models import User
from cloudinary_storage.storage import VideoMediaCloudinaryStorage

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    video = models.FileField(upload_to='event_videos/', null=True, blank=True, storage=VideoMediaCloudinaryStorage())
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class SignTranslationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='translation_history')
    original_text = models.CharField(max_length=1000)
    video_url = models.URLField(max_length=500)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.original_text[:20]}"
