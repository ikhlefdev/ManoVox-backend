from rest_framework import serializers  # <--- THIS IS THE MISSING LINE
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from django.contrib.auth import get_user_model
from .models import SignWord, User # Make sure User is imported here too!

User = get_user_model()

# We "Extend" Djoser's existing serializer
class UserRegistrationSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        # We combine Djoser's fields with your specific ones
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name','age')

    def create(self, validated_data):
        # This ensures passwords are encrypted properly in the database
        return User.objects.create_user(**validated_data)

class SignWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignWord
        fields = ['word', 'category', 'video_url', 'needs_ssl_bypass']