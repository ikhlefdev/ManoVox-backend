from rest_framework import serializers
from django.contrib.auth import get_user_model

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # We use create_user because it automatically handles password hashing
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user