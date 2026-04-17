from django.urls import path
from . import views
from .views import ASLLetterListView, send_reset_code, verify_and_reset_password

urlpatterns = [
    path('register_user/', views.UserRegistrationView.as_view(), name='register_user'),
    path('delete_account/', views.UserDeleteView.as_view(), name='delete_account'),   #as_view:take this class blueprint and turn it into a function that can handle a web request.
    path('sign_dictionary/', views.SignDictionaryView.as_view(), name='sign_dictionary'),
    # When the app requests /accounts/asl-letters/, trigger the ASLLetterListView
    path('asl-letters/', ASLLetterListView.as_view(), name='asl-letters'),
    
    path('api/custom-reset/send-code/', send_reset_code, name='send_code'),
    
    path('api/custom-reset/verify-code/', verify_and_reset_password, name='verify_code'),
]
