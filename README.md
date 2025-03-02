# CS-458 Project 1

## Installation

Ensure you have Python installed, then install the required dependencies:

```sh
pip install -r requirements.txt
```

## Running the Application

Start the application by running:

```sh
python app.py
```

## Running Tests

To execute the login tests, run:

```sh
python test_login.py
```

## Important Notes

- **Update Credentials:** Make sure to update `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `app.py` before running the application.
- **Database Setup:** The application requires a SQLite database (`users.db`). If it does not exist, it will be automatically created and seeded with a test user.
- **Login Methods:** The system supports authentication using both email and phone.
- **Google OAuth Support:** Ensure you have valid Google credentials configured for OAuth authentication.

---
