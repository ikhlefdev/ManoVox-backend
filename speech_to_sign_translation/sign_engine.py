import os
import re
import subprocess
import requests  # <-- New import!
import cloudinary
import cloudinary.uploader

# =========================
# PATHS
# =========================

cloudinary.config( 
  cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
  api_key = os.getenv("CLOUDINARY_API_KEY"), 
  api_secret = os.getenv("CLOUDINARY_API_SECRET") 
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WORDS_PATH = os.path.join(BASE_DIR, "dataset", "words")
LETTERS_PATH = os.path.join(BASE_DIR, "dataset", "letters")

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_PATH = os.path.join(OUTPUT_DIR, "final-video.mp4")
CLOUDINARY_BASE_URL = "https://res.cloudinary.com/dmjcq9wdh/video/upload"

# =========================
# STOP WORDS + NUMBERS
# =========================

STOP_WORDS = {
    "is", "am", "are", "was", "were",
    "the", "a", "an",
    "to", "of", "in", "on", "at",
    "for", "with", "about"
}

NUMBERS = {
    "0": "zero", "1": "one", "2": "two", "3": "three",
    "4": "four", "5": "five", "6": "six", "7": "seven",
    "8": "eight", "9": "nine", "10": "ten",
    "11": "eleven", "12": "twelve",
    "20": "twenty", "30": "thirty",
    "40": "forty", "50": "fifty",
    "100": "hundred"
}


# =========================
# TEXT NORMALIZATION
# =========================

def normalize_word(word):
    word = word.lower()
    word = re.sub(r"[^a-z0-9]", "", word)

    if word in NUMBERS:
        return NUMBERS[word]

    if word.endswith("ing") and len(word) > 4:
        word = word[:-3]
    elif word.endswith("ed") and len(word) > 3:
        word = word[:-2]
    elif word.endswith("es") and len(word) > 3:
        word = word[:-2]
    elif word.endswith("s") and len(word) > 3:
        word = word[:-1]

    return word


def normalize_text(text):
    text = re.sub(r"[^\w\s]", "", text)
    words = text.split()

    cleaned = []
    for w in words:
        nw = normalize_word(w)
        if nw and nw not in STOP_WORDS:
            cleaned.append(nw)

    print("🧠 Normalized words:", cleaned)
    return cleaned


# =========================
# MAP TEXT → VIDEOS
# =========================

def url_exists(url):
    """Checks if a video exists on Cloudinary using a streamed GET request to bypass blocks"""
    try:
        # Disguise as a standard Chrome browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Use GET with stream=True instead of HEAD. Cloudinary often blocks HEAD!
        response = requests.get(url, headers=headers, stream=True, allow_redirects=True)
        
        # If it fails, print EXACTLY why so we can fix it
        if response.status_code != 200:
            print(f"🕵️ Debug: Cloudinary returned {response.status_code} for {url}")
            return False
            
        return True
    except requests.RequestException as e:
        print(f"⚠️ Debug Request Error: {e}")
        return False

def get_video_sequence(words):
    video_urls = []

    for word in words:
        # --- THE FIX: Handle the "I" collision ---
        safe_word = "i_word" if word == "i" else word
        word_url = f"{CLOUDINARY_BASE_URL}/{safe_word}.mp4"
        # -----------------------------------------

        # Check if the word exists in Cloudinary 'words' folder
        if url_exists(word_url):
            video_urls.append(word_url)
            continue

        # If the word doesn't exist, spell it out using the 'letters' folder
        for letter in word:
            letter_url = f"{CLOUDINARY_BASE_URL}/{letter}.mp4"
            
            # SAFETY CHECK: Only add the letter if it actually exists!
            if url_exists(letter_url):
                video_urls.append(letter_url)
            else:
                print(f"⚠️ Warning: Missing letter video for '{letter}'")

    print("🎬 Video sequence URLs:", video_urls)
    return video_urls


# =========================
# CONCAT VIDEOS (FFMPEG)
# =========================

def concatenate_videos(video_paths):

    if not video_paths:
        raise ValueError("❌ No videos found to concatenate.")

    list_file = os.path.join(OUTPUT_DIR, "video_list.txt")

    with open(list_file, "w", encoding="utf-8") as f:
        for path in video_paths:
            f.write(f"file '{path}'\n")

    print("⚙️ Running FFmpeg...")

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-protocol_whitelist", "file,http,https,tcp,tls", # <-- MAGIC LINE FOR CLOUDINARY
        "-i", list_file,
        "-vf", "setpts=0.5*PTS",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "18",
        OUTPUT_PATH
    ]

    result = subprocess.run(cmd)

    if result.returncode != 0:
        raise RuntimeError("❌ FFmpeg failed")

    print("✅ Video created at:", OUTPUT_PATH)

    return OUTPUT_PATH

# =========================
# UPLOAD TO CLOUDINARY
# =========================

def upload_final_video(local_video_path):
    print("☁️ Uploading final video to Cloudinary...")
    
    try:
        # We upload it as a "video" and force the public_id to be "current_translation"
        # The 'overwrite=True' guarantees the old one gets deleted/replaced!
        response = cloudinary.uploader.upload(
            local_video_path,
            resource_type="video",
            public_id="current_translation",
            overwrite=True
        )
        
        cloud_url = response.get("secure_url")
        print(f"✅ Upload complete! Cloudinary URL: {cloud_url}")
        
        return cloud_url
        
    except Exception as e:
        print(f"❌ Cloudinary upload failed: {e}")
        return None

# =========================
# MAIN FUNCTION
# =========================

def text_to_sign(text):
    print("📥 Input text:", text)

    words = normalize_text(text)
    video_paths = get_video_sequence(words)

    # 1. Stitch the video locally
    local_video_path = concatenate_videos(video_paths)

    # 2. Upload it to Cloudinary
    final_cloudinary_url = upload_final_video(local_video_path)

    # 3. Return the cloud URL back to Django!
    return final_cloudinary_url
