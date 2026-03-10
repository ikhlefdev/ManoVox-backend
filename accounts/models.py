from django.db import models



# Create your models here.


class SignWord(models.Model):
    word = models.CharField(max_length=255)
    video_url = models.URLField(max_length=500)
    needs_ssl_bypass = models.BooleanField(default=False)
    category = models.CharField(max_length=100, default='General')

    

    def __str__(self):
        return self.word

    
    