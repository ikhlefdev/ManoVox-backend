import re
import os
import uuid
import tempfile
import cloudinary.uploader
from moviepy import VideoFileClip, concatenate_videoclips
from django.conf import settings

# -----------------------------
# Stop words
# -----------------------------
STOP_WORDS = {
    "is", "am", "are", "was", "were",
    "the", "a", "an",
    "to", "of", "in", "on", "at",
    "for", "with", "about"
}

# -----------------------------
# Number → word dictionary
# -----------------------------
NUMBERS = {
    "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
    "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
    "10": "ten", "11": "eleven", "12": "twelve", "13": "thirteen",
    "14": "fourteen", "15": "fifteen", "20": "twenty", "30": "thirty",
    "40": "forty", "50": "fifty", "100": "hundred"
}

def normalize_word(word):
    word = word.lower()
    # remove punctuation but KEEP numbers
    word = re.sub(r"[^a-z0-9]", "", word)

    if word in NUMBERS:
        return NUMBERS[word]

    # verb normalization
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
    cleaned_words = []

    for w in words:
        nw = normalize_word(w)
        if nw and nw not in STOP_WORDS:
            cleaned_words.append(nw)

    return " ".join(cleaned_words)


def text_to_sign_video(text, user_id, save_to_history=False):
    """
    Takes an input string, normalizes it, concatenates the mp4 files, 
    and uploads the final video to Cloudinary.
    """
    normalized = normalize_text(text)
    words = normalized.split()

    # Define internal server paths to the dataset
    BASE_MEDIA_PATH = os.path.join(settings.MEDIA_ROOT, 'sign_dataset_skeleton')
    WORDS_PATH = os.path.join(BASE_MEDIA_PATH, 'words')
    LETTERS_PATH = os.path.join(BASE_MEDIA_PATH, 'letters')

    video_clips = []

    for word in words:
        word_video = os.path.join(WORDS_PATH, f"{word}.mp4")

        # If full word video exists
        if os.path.exists(word_video):
            video_clips.append(VideoFileClip(word_video))
        else:
            # Drop down to letters
            for letter in word:
                letter_video = os.path.join(LETTERS_PATH, f"{letter}.mp4")
                if os.path.exists(letter_video):
                    video_clips.append(VideoFileClip(letter_video))

    if not video_clips:
        raise ValueError("No matching videos found in dataset for spelling or words.")

    # Generate a temporary file to save the stitched video using moviepy
    temp_dir = tempfile.gettempdir()
    local_output_path = os.path.join(temp_dir, f"temp_sign_{uuid.uuid4().hex}.mp4")

    # Stitch the clips together natively using python
    final_clip = concatenate_videoclips(video_clips, method="compose")
    
    # We write using libx264 for mobile compatibility and ultrafast preset
    final_clip.write_videofile(
        local_output_path, 
        codec="libx264", 
        preset="ultrafast",
        fps=24,
        logger=None # Suppress internal logs
    )

    # Close clips to free memory
    for clip in video_clips:
        clip.close()
    final_clip.close()

    # Upload to Cloudinary
    # If save_to_history is true, we give it a unique public_id so it is kept permanently.
    # If false, we overwrite the same file named "temp_translation_USERID" so we never waste space!
    
    if save_to_history:
        public_id = f"history_translation_user{user_id}_{uuid.uuid4().hex}"
    else:
        public_id = f"temp_translation_user{user_id}"

    upload_result = cloudinary.uploader.upload(
        local_output_path,
        resource_type="video",
        public_id=public_id,
        overwrite=True # This is the magic that deletes the old temp video!
    )

    # Delete the local temporary file from the python server
    if os.path.exists(local_output_path):
        os.remove(local_output_path)

    return upload_result['secure_url'], normalized
