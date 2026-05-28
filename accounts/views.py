from django.template.loader import render_to_string
from django.contrib.auth import get_user_model 
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserRegistrationSerializer , SignWordSerializer , ASLLetterSerializer
from .models import SignWord , ASLLetter , PasswordResetCode, EmailVerificationCode
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework import status
from .models import User, EmailVerificationCode

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
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]
    
    
@api_view(['POST'])
def send_reset_code(request):
    """Generates a 6-digit code and emails it to the user."""
    email = request.data.get('email')
    
    try:
        # Search the database for a user matching this email
        user = User.objects.get(email=email)
        
        reset_record = PasswordResetCode.objects.create(user=user)
        reset_record.generate_code()
        
        # 1. Grab the HTML file and inject the code into it
        html_content = render_to_string('email/otp_email.html', {'code': reset_record.code})
        
        # 2. Send the email with the new 'html_message' parameter
        send_mail(
            subject="Your ManoVox Password Reset Code",
            message=f"Your password reset code is: {reset_record.code}",
            from_email=None,
            recipient_list=[email],
            html_message=html_content
        )
        return Response({"message": "Code sent successfully!"}, status=200)
        
    except User.DoesNotExist:
        # Generic response to prevent email enumeration attacks
        return Response({"message": "If that email exists, a code was sent."}, status=200)


@api_view(['POST'])
def verify_and_reset_password(request):
    """Verifies the 6-digit code and updates the password."""
    # Extract the three pieces of data we need from the JSON body
    email = request.data.get('email')
    code = request.data.get('code')
    new_password = request.data.get('new_password')
    
    try:
        user = User.objects.get(email=email)
        reset_record = PasswordResetCode.objects.filter(user=user, code=code).last()
        
        if reset_record:
            user.set_password(new_password)
            user.save()
            reset_record.delete() # Invalidate code after use
            
            return Response({"message": "Password updated successfully!"}, status=200)
        
        return Response({"error": "Invalid code. Please try again."}, status=400)
            
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)
    


@api_view(['POST'])
def send_verification_code(request):
    email = request.data.get('email')
    
    try:
        user = User.objects.get(email=email)
        
        # If user is already active, no need to send a code
        if user.is_active:
            return Response({"message": "Account is already verified."}, status=400)

        # Create and generate the code
        verification_record = EmailVerificationCode.objects.create(user=user)
        verification_record.generate_code()
        
        # Render the HTML template
        html_content = render_to_string('email/verify_email.html', {'code': verification_record.code})
        
        # Send the email
        send_mail(
            subject="Verify your ManoVox Account",
            message=f"Your verification code is: {verification_record.code}",
            from_email=None,
            recipient_list=[email],
            html_message=html_content
        )
        
        return Response({"message": "Verification code sent successfully!"}, status=200)
        
    except User.DoesNotExist:
        # We still return 200 to prevent email enumeration (security best practice)
        return Response({"message": "If that email exists, a code was sent."}, status=200)


@api_view(['POST'])
def verify_email(request):
    email = request.data.get('email')
    code = request.data.get('code')
    
    if not email or not code:
        return Response({"error": "Email and code are required."}, status=400)
        
    try:
        user = User.objects.get(email=email)
        
        # Find the latest code for this user
        verification_record = EmailVerificationCode.objects.filter(user=user, code=code).last()
        
        if verification_record:
            # Activate the user!
            user.is_active = True
            user.save()
            
            # Delete the code so it can't be reused
            verification_record.delete()
            
            return Response({"message": "Email verified successfully!"}, status=200)
        else:
            return Response({"error": "Invalid code."}, status=400)
            
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)
    
class VerifyEmailView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        try:
            # Find the user and the code record
            user = User.objects.get(email=email)
            verification = EmailVerificationCode.objects.get(user=user, code=code)

            # 1. Activate the user
            user.is_active = True
            user.save()

            # 2. Delete the code so it can't be used again
            verification.delete()

            return Response({"message": "Account activated successfully!"}, status=status.HTTP_200_OK)

        except (User.DoesNotExist, EmailVerificationCode.DoesNotExist):
            return Response({"error": "Invalid email or verification code."}, status=status.HTTP_400_BAD_REQUEST)

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
