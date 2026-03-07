from django.urls import path
from . import views

urlpatterns = [
    path('register_user/', views.UserRegistrationView.as_view(), name='register_user'),
    path('delete_account/', views.UserDeleteView.as_view(), name='delete_account'),   #as_view:take this class blueprint and turn it into a function that can handle a web request.
]
