import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from deaf_hub.ai_translation import text_to_sign_video

def run_test():
    try:
        print("Starting video generation test...")
        # Since this tests the raw logic, the user ID 999 is just a placeholder
        # and save_to_history=False means it will be uploaded as temp_translation_user999
        url, normalized = text_to_sign_video("hi", user_id=999, save_to_history=False)
        print("✅ SUCCESS!")
        print(f"Normalized Text Used: '{normalized}'")
        print(f"Cloudinary Video URL: {url}")
    except Exception as e:
        print("❌ FAILED:")
        print(str(e))

if __name__ == "__main__":
    run_test()
