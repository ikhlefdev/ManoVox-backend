from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, TextToSignView, TranslationHistoryView, ToggleFavoriteView

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
    path('translate/', TextToSignView.as_view(), name='translate-to-sign'),
    path('translation-history/', TranslationHistoryView.as_view(), name='translation-history'),
    path('translation-history/<int:history_id>/favorite/', ToggleFavoriteView.as_view(), name='toggle-favorite'),
]
