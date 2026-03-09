# ManoVox - Backend

This is the Django-based backend for the ManoVox communication app. 


## Tech Stack
- **Framework:** Django 6.0.3
- **API:** Django REST Framework
- **Auth:** Djoser & Token Authentication (DRF tokens)
- **Email:** Gmail SMTP Integration

## Features Implemented
- **User Registration:** Secure account creation via `POST`.
- **Account Deletion:** Self-service account removal via `DELETE`.
- **CORS configuration:** Configured for mobile/Flutter integration.
- **SQL Database:** Integrated user management system.
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
    "email": "user@mail.com"
  }

### 1. Delete account
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
    "username": "example_user",
    "password": "yourpassword123"
  }

### 4. Request Password Reset
- **URL:** `/auth/users/reset_password/`
- **Method:** `POST`
- **Description:** Sends a password reset link to the user's registered email.
- **Body:**
  ```json
  {
    "email": "user@mail.com"
  }

### 5. Confirm password
- **URL:** `/auth/users/reset_password_confirm/`
- **Method:** `POST`
- **Description:** completes the password change using the uid and token from the email
- **Body:**
  ```json
  {
    "uid": "encoded_user_id",
    "token": "reset_token",
    "new_password": "newpassword123",
    "re_new_password": "newpassword123"
  }

### 6. Log out
- **URL:** `/auth/token/logout/`
- **Method:** `POST`
- **Description:** deletes the token on the server side to end the session
- **Headers:** - `Authorization`: `Token <your_token_string>`
- **Security:** Requires Token authentication.