from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserRegistrationSerializer , SignWordSerializer , ASLLetterSerializer
from .models import SignWord , ASLLetter

User = get_user_model()

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
    
# This view handles the logic for sending a list of all ASL letters to the frontend.
class ASLLetterListView(generics.ListAPIView):
    # 1. Grab all the letters from the database and sort them alphabetically (A-Z)
    queryset = ASLLetter.objects.all().order_by('letter')
    
    # 2. Pass those letters through our translator so they become JSON
    serializer_class = ASLLetterSerializer

from rest_framework.views import APIView
import numpy as np
from .preprocess import preprocess
from .inference import TFLiteASLModel

class PredictASLView(APIView):
    """
    Classifies a sequence of 64 frames of MediaPipe Holistic landmarks (114 landmarks * 3 coordinates).
    Expects request format: {"sequence": [[x, y, z, ...], [x, y, z, ...], ...]} of shape (64, 342)
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        sequence_data = request.data.get('sequence')
        
        if not sequence_data:
            return Response(
                {"error": "Missing 'sequence' field in request data."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Convert to numpy array
            seq = np.array(sequence_data, dtype=np.float32)
            
            # Check shape
            if seq.shape != (64, 342):
                return Response(
                    {"error": f"Invalid sequence shape: expected (64, 342) but got {seq.shape}."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Reshape sequence to match dominant_hand_normalize expectations (64, 114, 3)
            seq_reshaped = seq.reshape(64, 114, 3)
            
            # Preprocess the landmarks using the exact training code
            processed = preprocess(seq_reshaped)  # (64, 1026)
            
            # Load the model and predict
            predicted_class, confidence = TFLiteASLModel.get_instance().predict(processed)
            
            return Response({
                "class": predicted_class,
                "confidence": round(confidence, 4)
            }, status=status.HTTP_200_OK)
            
        except ValueError as ve:
            return Response(
                {"error": f"Value error during processing: {str(ve)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to perform prediction: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )