from rest_framework import serializers
from .models import Event
from accounts.serializers import UserRegistrationSerializer

class EventSerializer(serializers.ModelSerializer):
    author_info = UserRegistrationSerializer(source='author', read_only=True)
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'image', 'video', 'date', 'location', 'author', 'author_info', 'created_at']
        read_only_fields = ['author', 'created_at']

from .models import SignTranslationHistory

class SignTranslationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SignTranslationHistory
        fields = ['id', 'user', 'original_text', 'video_url', 'is_favorite', 'created_at']
        read_only_fields = ['user', 'created_at']
