"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from speech_to_sign_translation.views import translate_audio, toggle_favorite
from speech_to_sign_translation import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("",include('accounts.urls')),
    
    path('auth/', include('djoser.urls')),           # Djoser: Forgot Password, Reset Password, Register
    path('auth/', include('djoser.urls.authtoken')), # Djoser: Login (get token) and Logout (destroy token)
    path('api/deaf-hub/', include('deaf_hub.urls')),
    # Front end's endpoint pointing directly to the new app
    path('speech-to-sign-audio/', views.translate_audio, name='translate_audio'),
    path('favorite/<int:history_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('delete-history/<int:history_id>/', views.delete_history_item, name='delete_history'),
    #to see the whole history list
    path('history-list/', views.get_history_list, name='history_list'),
]

# This tells Django: "While we are building the app (DEBUG mode), please serve the media files!"
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
