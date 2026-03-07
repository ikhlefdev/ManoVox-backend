# ManoVox - Backend

This is the Django-based backend for the ManoVox communication app. 


## Tech Stack
- **Framework:** Django 6.0.3
- **API:** Django REST Framework
- **Auth:** JWT (JSON Web Tokens)

## Features Implemented
- **User Registration:** Secure account creation via `POST`.
- **Account Deletion:** Self-service account removal via `DELETE`.
- **CORS configuration:** Configured for mobile/Flutter integration.
- **SQL Database:** Integrated user management system.


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
