# ManoVox - Backend

This is the Django-based backend for the ManoVox communication app. 


## Tech Stack
- **Framework:** Django 6.0.3
- **API:** Django REST Framework
- **Database:** Neon PostgreSQL (Cloud Shared Database)
- **Media Storage:** Cloudinary (Cloud Video & Image Hosting)
- **Auth:** Djoser & Token Authentication (DRF tokens)
- **Email:** Gmail SMTP Integration

## Features Implemented
- **User Registration:** Secure account creation via `POST`.
- **Account Deletion:** Self-service account removal via `DELETE`.
- **CORS configuration:** Configured for mobile/Flutter integration.
- **Cloud Database (Neon PostgreSQL):** Integrated, shared remote database for real-time syncing.
- **Cloud Media (Cloudinary):** Seamless cloud hosting for scalable image and video serving.
- **User Authentication:** Complete registration, login, and logout flow using Djoser.
- **Password Recovery:** Automated "Forgot Password" system via Gmail SMTP.
- **Security:** Sensitive keys and credentials managed via `.env` variables.


## 🛠 API Documentation (Accounts)

### 1. Register User
- **URL:** `/accounts/register/`
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
- **URL:** `/accounts/delete_account/`
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
- **Query Parameters:** 
  - `?search=<word>` (optional)
  - `?category=<category>` (optional)

### 7. Get ASL Letters
- **URL:** `/accounts/asl-letters/`
- **Method:** `GET`
- **Description:** Retrieves all letters of the ASL alphabet along with their corresponding cloud-hosted image and video URLs.