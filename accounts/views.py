from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserRegistrationSerializer , SignWordSerializer
from .models import SignWord

# --- REGISTRATION ---
class UserRegistrationView(generics.CreateAPIView):
    """
    Handles user creation using OOP principles.
    Inherits from CreateAPIView to handle POST requests automatically.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # We 'Override' the create method to add our custom success message
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            "message": "User created successfully",
            "user": serializer.data
        }, status=status.HTTP_201_CREATED)


# --- DELETE ACCOUNT ---
class UserDeleteView(generics.DestroyAPIView):
    """
    Handles account removal.
    Inherits from DestroyAPIView to handle DELETE requests.
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Encapsulation: The logic for 'which object to delete' 
        # is hidden inside this method.
        return self.request.user

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response(
            {"message": "Account deleted successfully!"}, 
            status=status.HTTP_200_OK
        )
class SignDictionaryView(generics.ListAPIView):
    serializer_class = SignWordSerializer

    def get_queryset(self):
        queryset = SignWord.objects.all()
        # This catches the word the user types in the search bar
        word = self.request.query_params.get('search')
        category = self.request.query_params.get('category')
        # Apply search if provided
        if word:
            queryset = queryset.filter(word__icontains=word)
            
        # Apply category if provided
        if category:
            # Using '__iexact' so 'food' matches 'Food'
            queryset = queryset.filter(category__iexact=category)
            
        return queryset