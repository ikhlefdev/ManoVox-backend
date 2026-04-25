from rest_framework import viewsets, permissions
from .models import Event
from .serializers import EventSerializer

class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from .models import SignTranslationHistory
from .serializers import SignTranslationHistorySerializer
from .ai_translation import text_to_sign_video

class TextToSignView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        text = request.data.get('text')
        save_to_history = request.data.get('save_to_history', False)

        if not text:
            return Response({"error": "text is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # We call our internal ai_translation tool
            video_url, normalized_text = text_to_sign_video(
                text=text, 
                user_id=request.user.id, 
                save_to_history=save_to_history
            )

            response_data = {
                "original_text": text,
                "normalized_text": normalized_text,
                "video_url": video_url,
                "saved_to_history": save_to_history
            }

            # If user wants to save it to their permanent history
            if save_to_history:
                history_record = SignTranslationHistory.objects.create(
                    user=request.user,
                    original_text=text,
                    video_url=video_url,
                    is_favorite=False
                )
                serializer = SignTranslationHistorySerializer(history_record)
                response_data['history_record'] = serializer.data

            return Response(response_data, status=status.HTTP_200_OK)

        except ValueError as e:
            # If a word/letter has no corresponding video in the dataset
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Failed to generate translation: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TranslationHistoryView(generics.ListAPIView):
    serializer_class = SignTranslationHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return the history for the currently logged in user
        queryset = SignTranslationHistory.objects.filter(user=self.request.user)
        
        # If the frontend passes ?favorite=true, we filter the list!
        favorite = self.request.query_params.get('favorite')
        if favorite and favorite.lower() == 'true':
            queryset = queryset.filter(is_favorite=True)
            
        return queryset


class ToggleFavoriteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, history_id):
        # Make sure this specific translation actually belongs to the user trying to favorite it!
        history_record = get_object_or_404(SignTranslationHistory, id=history_id, user=request.user)
        
        # Flip the boolean
        history_record.is_favorite = not history_record.is_favorite
        history_record.save()
        
        return Response({
            "message": "Favorite status updated",
            "is_favorite": history_record.is_favorite
        }, status=status.HTTP_200_OK)
