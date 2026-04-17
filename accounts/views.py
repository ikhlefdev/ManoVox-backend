from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserRegistrationSerializer , SignWordSerializer , ASLLetterSerializer
from .models import SignWord , ASLLetter , PasswordResetCode
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

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