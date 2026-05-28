from django.urls import path
from . import views
from .views import (
    ASLLetterListView, 
    send_reset_code, 
    verify_and_reset_password, 
    send_verification_code, 
    verify_email, 
    UserRegistrationView, 
    VerifyEmailView
)

urlpatterns = [
    path('register_user/', views.UserRegistrationView.as_view(), name='register_user'),
    path('delete_account/', views.UserDeleteView.as_view(), name='delete_account'),   #as_view:take this class blueprint and turn it into a function that can handle a web request.
    path('sign_dictionary/', views.SignDictionaryView.as_view(), name='sign_dictionary'),
    # When the app requests /accounts/asl-letters/, trigger the ASLLetterListView
    path('asl-letters/', ASLLetterListView.as_view(), name='asl-letters'),
    path('predict/', views.PredictASLView.as_view(), name='predict'),
    
    path('api/custom-reset/send-code/', send_reset_code, name='send_code'),
    path('api/custom-reset/verify-code/', verify_and_reset_password, name='verify_code'),
    
    path('custom-verify/send-code/', send_verification_code, name='send-verification-code'),
    path('custom-verify/verify-email/', verify_email, name='verify-email'),
    
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
]
