# ArabDabha Backend (Django + DRF)

A RESTful API backend for a restaurant store, built with Django and Django REST Framework. This document describes what’s implemented so far (focus: authentication), how to run it, and how to work with the endpoints.


## Overview

- Frameworks: Django 5.2, DRF 3.16, Simple JWT
- Apps:
  - `apps.users`: custom user model, auth endpoints, email verification/password reset
- Auth style: Access token in response body, Refresh token in HttpOnly cookie
- Email: verification and password reset emails via Django’s `EmailMultiAlternatives`


## Project Structure

```
core/
  settings.py, urls.py, asgi.py, wsgi.py
apps/
  users/
    models.py, serializers.py, views.py, urls.py, auth.py
    services/
      email_service.py, verification_service.py, token_service.py
    utils/
      email_templates.py
manage.py
requirements.txt
```


## Setup

1) Environment variables (using python-decouple):

- Core
  - `SECRET_KEY`
  - `DEBUG` (bool)
  - `ALLOWED_HOSTS` (CSV, e.g. `127.0.0.1,localhost`)
- Database
  - `DB_ENGINE` (default `django.db.backends.sqlite3`)
  - `DB_NAME` (default `db.sqlite3`)
- JWT
  - `ACCESS_TOKEN_LIFETIME_MINUTES` (default 15)
  - `REFRESH_TOKEN_LIFETIME_DAYS` (default 7)
  - `ROTATE_REFRESH_TOKENS` (default False)
  - `BLACKLIST_AFTER_ROTATION` (default True)
  - `AUTH_HEADER_TYPES` (default `Bearer`)
  - `UPDATE_LAST_LOGIN` (default True)
- Email
  - `EMAIL_BACKEND`
  - `EMAIL_HOST`
  - `EMAIL_PORT` (default 587)
  - `EMAIL_USE_TLS` (default True)
  - `EMAIL_USE_SSL` (default False)
  - `EMAIL_HOST_USER`
  - `DEFAULT_FROM_EMAIL`
  - `EMAIL_HOST_PASSWORD`
  - `EMAIL_TOKEN_RESET_TIMEOUT` (seconds; default 120; used via custom generator timeout)

2) Install dependencies

- See `requirements.txt` (Django, DRF, Simple JWT, CORS headers, python-decouple).

3) Migrate and run

- Apply migrations
- Create a superuser (optional)
- Run the dev server (default port 8000)

4) Admin

- `/admin/` for Django admin (custom User admin registered).


## Authentication Design

- Custom User model (`apps.users.models.User`)
  - Email as username (`USERNAME_FIELD = "email"`)
  - Roles: ADMIN, STAFF, CUSTOMER
  - Email uniqueness enforced case-insensitively (index + constraint using `Lower("email")`)
  - Fields: `email`, `full_name`, `is_email_verified`, `is_active`, `is_staff`, `date_joined`, `last_login`

- Tokens (Simple JWT)
  - Login returns `access` in response body
  - `refresh` is removed from body and set as `refresh_token` HttpOnly cookie
  - Refresh endpoint reads `refresh_token` from cookie and returns a new `access`
  - Blacklist is enabled, and logout tries to blacklist the cookie’s refresh token

- Email flows
  - Verification: On register, an email with a tokenized URL is sent; visiting it sets `is_email_verified=True`
  - Password reset: Request sends a reset email link; resetting validates token and updates password


## Endpoints

Base path: `/api/v1/` (see `core/urls.py` and `apps/users/urls.py`)

- `GET /api/v1/auth/me/` — Get current user profile
  - Auth: `Authorization: Bearer <access>`
  - Response: `id, email, full_name, role, is_email_verified, date_joined, last_login`

- `PATCH /api/v1/auth/me/` — Update profile (currently `full_name` only)
  - Body: `{ "full_name": "..." }`

- `POST /api/v1/auth/register/` — Register user
  - Body: `{ "email": "...", "password": "..." }`
  - Side effects: sends verification email

- `GET /api/v1/auth/verify_email/<uidb64>/<token>/` — Verify email link
  - Marks `is_email_verified=True` when token is valid

- `POST /api/v1/auth/login/` — Obtain tokens
  - Body: `{ "email": "...", "password": "..." }`
  - Response body: `{ "access": "...", ...custom claims }`
  - Side effect: sets `refresh_token` cookie (HttpOnly)

- `POST /api/v1/auth/refresh/` — Refresh access token
  - Reads `refresh_token` cookie and returns `{ "access": "..." }`

- `POST /api/v1/auth/change-password/` — Change password (authenticated)
  - Body: `{ "old_password": "...", "new_password": "..." }`

- `POST /api/v1/auth/logout/` — Logout (authenticated)
  - Tries to blacklist refresh and clears cookie

- `POST /api/v1/auth/forgot-password/` — Request password reset
  - Body: `{ "email": "..." }`
  - Always returns generic success to avoid user enumeration

- `POST /api/v1/auth/reset-password/<uidb64>/<token>/` — Reset password
  - Body: `{ "new_password": "..." }`


## Implementation Notes

- Cookie handling (`apps/users/auth.py`)
  - Sets cookie: name `refresh_token`, `httponly=True`, `samesite="Lax"`, `secure=False` (dev), `max_age=7 days`, `path="/api/v1/auth"`
  - Clears cookie on logout (same path)
  - For cross-site usage in production, set `samesite="None"` and `secure=True` over HTTPS

- JWT claims (`RoleTokenObtainPairSerializer`)
  - Adds `role`, `email`, and `is_email_verified` to token payload

- `last_login`
  - `SIMPLE_JWT["UPDATE_LAST_LOGIN"] = True` means successful token obtain will update `last_login`

- Email services
  - `VerificationService` builds absolute URLs from incoming `request` and sends emails using templates in `utils/email_templates.py`
  - Available templates: verification, welcome, password reset (welcome not yet invoked in registration flow)


## Local Dev Tips (Postman / Cookies)

- Keep domain and port consistent (e.g., use only `http://localhost:8000` everywhere)
- Postman stores cookies per domain; verify `refresh_token` under the exact domain
- For local HTTP, keep `secure=False` and `samesite="Lax"` so cookies are sent on same-site navigations/API calls
- If cookies aren’t sent automatically, you can manually add a `Cookie` header: `refresh_token=<value>`


## Security Considerations (current)

- HttpOnly refresh cookie; blacklist on logout
- Generic responses for forgot-password to avoid user enumeration
- Recommendations:
  - Place `corsheaders.middleware.CorsMiddleware` near the top of `MIDDLEWARE` for correctness
  - In production use HTTPS, set cookie `secure=True` and `samesite="None"`
  - Consider rate-limiting login/forgot/reset endpoints
  - Add explicit CSRF strategy if introducing session auth anywhere
  - Increase `EMAIL_TOKEN_RESET_TIMEOUT` for real-world flows (24h common)


## Roadmap / Next Steps

- User profile model/fields expansion (address, phone, avatar, preferences)
- Welcome email on successful email verification or registration
- Admin/Staff roles permissions and endpoints for store management
- Pagination/filters for future resources (menus, orders, etc.)
- Add automated tests under `apps/users/tests.py`
- Production hardening: security headers, logging, monitoring


## Troubleshooting

- Cookie not received in refresh:
  - Ensure same domain/port; check Postman cookie jar; match cookie `path` (`/api/v1/auth`)
  - For cross-site tests use HTTPS + `SameSite=None` + `Secure=True`
- Emails not sending:
  - Verify email settings and credentials; check SMTP logs


## License

Private project (license not specified). Add a license if/when this is open-sourced.
