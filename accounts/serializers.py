from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SignWord

class UserRegistrationSerializer(serializers.ModelSerializer):
    # We add these to make them required and clear
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    class Meta:
        model = get_user_model()
       # We add 'id' here so the frontend can 'read' it after registration
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # We use create_user because it automatically handles password hashing
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user
class SignWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignWord
        fields = ['word', 'category','video_url', 'needs_ssl_bypass']
    
