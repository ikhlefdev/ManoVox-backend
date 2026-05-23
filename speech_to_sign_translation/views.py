import os
import whisper
import cloudinary.uploader
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from .sign_engine import text_to_sign
from .models import TranslationHistory

model = whisper.load_model("base")

@csrf_exempt
def translate_audio(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        
        # Amina sends 'save_to_history' = 'true' if the user clicked "Save"
        should_save = request.POST.get('save_to_history') == 'true'
        
        fs = FileSystemStorage()
        file_name = fs.save(f"temp_{audio_file.name}", audio_file)
        file_path = fs.path(file_name)
        
        try:
            # 1. Transcribe
            result = model.transcribe(file_path, fp16=False)
            transcribed_text = result["text"]
            
            # 2. Stitch Video
            final_video_path = text_to_sign(transcribed_text)
            
            # 3. Handle Cloudinary Upload
            if should_save:
                # UNIQUE UPLOAD: Stays in history
                upload_response = cloudinary.uploader.upload(
                    final_video_path,
                    resource_type="video",
                    folder="translated_signs/history"
                )
            else:
                # OVERWRITE UPLOAD: Replaces the user's specific temp slot
                user_slot = f"temp_user_{request.user.id}" if request.user.is_authenticated else "guest_temp"
                upload_response = cloudinary.uploader.upload(
                    final_video_path,
                    resource_type="video",
                    folder="translated_signs/temp",
                    public_id=user_slot,
                    overwrite=True,
                    invalidate=True 
                )

            video_url = upload_response.get("secure_url")

            # 4. Handle Database
            history_id = None
            if should_save:
                history_entry = TranslationHistory.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    original_text=transcribed_text,
                    video_url=video_url
                )
                history_id = history_entry.id

        finally:
            if os.path.exists(file_path): os.remove(file_path)
            if 'final_video_path' in locals() and os.path.exists(final_video_path):
                os.remove(final_video_path)
                
        return JsonResponse({
            "id": history_id,
            "text": transcribed_text,
            "video_url": video_url,
            "saved": should_save
        })
        
    return JsonResponse({"error": "No audio file found in the request"}, status=400)


@csrf_exempt
def delete_history_item(request, history_id):
    """Allows user to delete things they previously saved"""
    if request.method == 'DELETE' or request.method == 'POST':
        try:
            entry = TranslationHistory.objects.get(id=history_id)
            
            # Extract Cloudinary Public ID to delete the actual video file
            public_id = "translated_signs/history/" + entry.video_url.split('/')[-1].split('.')[0]
            
            cloudinary.uploader.destroy(public_id, resource_type="video")
            entry.delete()
            
            return JsonResponse({"status": "success"})
        except TranslationHistory.DoesNotExist:
            return JsonResponse({"error": "Not found"}, status=404)
            
    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def toggle_favorite(request, history_id):
    """Allows Flutter to heart/unheart a saved translation"""
    if request.method == 'POST':
        try:
            entry = TranslationHistory.objects.get(id=history_id)
            entry.is_favorite = not entry.is_favorite
            entry.save()
            return JsonResponse({"status": "success", "is_favorite": entry.is_favorite})
        except TranslationHistory.DoesNotExist:
            return JsonResponse({"error": "Item not found"}, status=404)
            
    return JsonResponse({"error": "Invalid request method"}, status=400)


def get_history_list(request):
    """Sends the whole list of saved translations to Flutter"""
    
    # Check if the user is actually logged in
    if not request.user.is_authenticated:
        return JsonResponse({"history": []}) # Guests don't have a saved history!
        
    # ONLY get the history for the logged-in user
    history = TranslationHistory.objects.filter(user=request.user).order_by('-created_at')
    
    # Temporarily use this so Postman can see everything!
    #history = TranslationHistory.objects.all().order_by('-created_at')
    
    data = []
    for item in history:
        data.append({
            "id": item.id,
            "text": item.original_text,
            "video_url": item.video_url,
            "is_favorite": item.is_favorite,
            "date": item.created_at.strftime("%Y-%m-%d")
        })
        
    return JsonResponse({"history": data})