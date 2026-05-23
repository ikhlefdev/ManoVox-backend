# ManoVox - Backend

This is the Django-based backend for the ManoVox communication app. 


## Tech Stack
- **Framework:** Django 6.0.3
- **API:** Django REST Framework
- **Database:** Neon PostgreSQL (Cloud Shared Database)
- **Media Storage:** Cloudinary (Cloud Video & Image Hosting)
- **Auth:** Djoser & Token Authentication (DRF tokens)
- **Email:** Gmail SMTP Integration
- **AI Transcription:** OpenAI Whisper (Speech-to-Text)
- **Video Processing:** FFmpeg (Dynamic Video Concatenation)

## Features Implemented
- **User Registration:** Secure account creation via `POST`.
- **Account Deletion:** Self-service account removal via `DELETE`.
- **CORS configuration:** Configured for mobile/Flutter integration.
- **Cloud Database (Neon PostgreSQL):** Integrated, shared remote database for real-time syncing.
- **Cloud Media (Cloudinary):** Seamless cloud hosting for scalable image and video serving.
- **User Authentication:** Complete registration, login, and logout flow using Djoser.
- **Email Verification:** Automated OTP confirmation code sent to users upon registration to activate accounts.
- **Password Recovery:** Automated "Forgot Password" system via Gmail SMTP.
- **Security:** Sensitive keys and credentials managed via `.env` variables.
- **Deaf Hub:** Event feed allowing specific administration accounts to create, manage, and share events with regular users.
- **Speech-to-Sign Engine:** Transcribes audio via Whisper, normalizes text, maps to individual ASL video signs/letters, stitches them into a cohesive video using FFmpeg, and hosts on Cloudinary.
- **Translation History:** Allows authenticated users to optionally save their generated signs, view past translations, toggle favorites, and securely delete videos from both the database and cloud storage.


## 🛠 API Documentation (Accounts)

### 1. Register User
- **URL:** `/register_user/`
- **Method:** `POST`
- **Description:** Creates a new user in the database.
- **Body:**
  ```json
  {
    "first_name":"example_first_name",
    "last_name":"example_last_name",
    "username": "example_user",
    "password": "yourpassword123",
    "email": "user@mail.com",
    "age": "example_age"
  }
### 2. Delete account
- **URL:** `/delete_account/`
- **Method:** `DELETE`
- **Description:** deletes a user from the database
- **Security:** Requires Bearer Token authentication.

### 3. Login User
- **URL:** `/auth/token/login/`
- **Method:** `POST`
- **Description:** Exchanges user credentials for an authentication token.
- **Body:**
  ```json
  {
    "email": "example_user",
    "password": "yourpassword123"
  }

### 4. Password Reset Flow

**Step 1: Request Reset Code**
- **URL:** `/api/custom-reset/send-code/`
- **Method:** `POST`
- **Description:** Generates a 6-digit OTP (One-Time Password) and sends it to the user's registered email in an HTML template.
- **Body:**
  ```json
  {
    "email": "user@mail.com"
  }
  ```

**Step 2: Verify Code and Reset Password**
- **URL:** `/api/custom-reset/verify-code/`
- **Method:** `POST`
- **Description:** Verifies the 6-digit code provided by the user. If valid, it updates the user's password and invalidates the code so it cannot be reused.
- **Body:**
  ```json
  {
    "email": "user@mail.com",
    "code": "123456",
    "new_password": "NewSecurePassword123!"
  }
  ```

### 5. Log out
- **URL:** `/auth/token/logout/`
- **Method:** `POST`
- **Description:** deletes the token on the server side to end the session
- **Headers:** - `Authorization`: `Token <your_token_string>`
- **Security:** Requires Token authentication.

### 6. Get ASL Sign Dictionary
- **URL:** `/accounts/sign_dictionary/`
- **Method:** `GET`
- **Description:** Retrieves a list of ASL sign words. Supports searching and category filtering via query parameters.
- **Security:** Public (`AllowAny`), no token required for frontend integration.
- **Query Parameters:** 
  - `?search=<word>` (optional)
  - `?category=<category>` (optional)

### 7. Get ASL Letters
- **URL:** `/accounts/asl-letters/`
- **Method:** `GET`
- **Description:** Retrieves all letters of the ASL alphabet along with their corresponding cloud-hosted image and video URLs.
- **Security:** Public (`AllowAny`), no token required for frontend integration.

### 8. Email Verification Flow

**Step 1: Request Verification Code**
- **URL:** `/accounts/custom-verify/send-code/`
- **Method:** `POST`
- **Description:** Generates a 6-digit OTP and sends it to the user's email in an HTML template.
- **Body:**
  ```json
  {
    "email": "user@mail.com"
  }
  ```

**Step 2: Verify Code and Activate Account**
- **URL:** `/accounts/custom-verify/verify-email/`
- **Method:** `POST`
- **Description:** Verifies the 6-digit code. If valid, the user's account is activated (`is_active=True`) and the code is deleted.
- **Body:**
  ```json
  {
    "email": "user@mail.com",
    "code": "123456"
  }
  ```

---

## 📅 API Documentation (Deaf Hub)

### 1. Fetch Deaf Hub Event Feed
- **URL:** `/api/deaf-hub/events/`
- **Method:** `GET`
- **Description:** Returns an array of Event objects.

### 2. Create a New Event
- **URL:** `/api/deaf-hub/events/`
- **Method:** `POST`
- **Headers:** `Authorization: Token <your_token_string>`
- **Description:** Creates a new event. The user MUST be registered with `"role": "admin"`.
- **Payload fields:** `title`, `description`, `date`, `location`, `image` (optional), `video` (optional).

## 🗣️ API Documentation (Speech-to-Sign Translation)

### 1. Translate Audio to ASL Video
- **URL:** `/speech-to-sign-audio/`
- **Method:** `POST`
- **Description:** Receives an audio file, transcribes it using Whisper, stitches the corresponding ASL videos together via FFmpeg, and uploads the final result to Cloudinary.
- **Body (`form-data`):**
  - `audio`: The uploaded audio file (e.g., .mp3, .wav).
  - `save_to_history`: `"true"` or `"false"` (Determines if the video is saved permanently to the user's history or overwritten in a temporary slot).

### 2. Get Translation History
- **URL:** `/history-list/`
- **Method:** `GET`
- **Description:** Retrieves a list of the user's securely saved translations (text, video URL, date, and favorite status).
- **Security:** Requires Token authentication (filters by the logged-in user).

### 3. Toggle Favorite Status
- **URL:** `/favorite/<int:history_id>/`
- **Method:** `POST`
- **Description:** Toggles the `is_favorite` boolean (heart/unheart) for a specific saved translation.

### 4. Delete Saved Translation
- **URL:** `/delete-history/<int:history_id>/`
- **Method:** `DELETE` (or `POST`)
- **Description:** Deletes the translation history record from the database and permanently removes the associated video file from Cloudinary storage to free up space.