from django.urls import path
from . import views
from .views import ASLLetterListView

urlpatterns = [
    path('register_user/', views.UserRegistrationView.as_view(), name='register_user'),
    path('delete_account/', views.UserDeleteView.as_view(), name='delete_account'),   #as_view:take this class blueprint and turn it into a function that can handle a web request.
    path('sign_dictionary/', views.SignDictionaryView.as_view(), name='sign_dictionary'),
    # When the app requests /accounts/asl-letters/, trigger the ASLLetterListView
    path('asl-letters/', ASLLetterListView.as_view(), name='asl-letters'),
    path('predict/', views.PredictASLView.as_view(), name='predict'),
]
