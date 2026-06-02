from rest_framework import serializers  # <--- THIS IS THE MISSING LINE
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from django.contrib.auth import get_user_model
from .models import SignWord, User, SignPredictionHistory # Make sure User is imported here too!
from .models import ASLLetter

User = get_user_model()

# We "Extend" Djoser's existing serializer
class UserRegistrationSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        # We combine Djoser's fields with your specific ones
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'age', 'role', 'organization_name', 'phone_number')

    def create(self, validated_data):
        # This ensures passwords are encrypted properly in the database
        return User.objects.create_user(**validated_data)

class SignWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignWord
        fields = ['word', 'category', 'video_url', 'needs_ssl_bypass']
        
        
# This translates our ASLLetter database model into JSON data 
# so the frontend (React/Flutter/etc.) can actually read it.
class ASLLetterSerializer(serializers.ModelSerializer):
    # 1. We tell Django: "Let me handle the image field manually"
    image = serializers.SerializerMethodField()

    class Meta:
        model = ASLLetter
        fields = ['id', 'letter', 'image', 'video']

    # 2. We construct the perfect, clean URL for the frontend
    def get_image(self, obj):
        if obj.image:
            return f"https://res.cloudinary.com/dmjcq9wdh/image/upload/Sign_Language_{obj.letter.upper()}.jpg"
        return None


class SignPredictionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SignPredictionHistory
        fields = ['id', 'predicted_text', 'confidence', 'video_url', 'created_at']
