# Insighta Web Portal

## Overview

This repository contains the **Insighta Web Portal**, a Django-based
frontend that connects to the Insighta backend API.

-   Built with **Django templates (no React)**
-   Uses **session-based authentication**
-   Integrates with backend via **HTTP (httpx)**
-   Supports **GitHub OAuth login**
-   Designed as a clean production-style UI layer

------------------------------------------------------------------------

## Project Structure

    insighta-web/
    ├── web/
    │   ├── templates/
    │   ├── views.py
    │   ├── urls.py
    │   └── middleware.py
    ├── portal/
    │   └── settings.py
    └── requirements.txt

------------------------------------------------------------------------

## Features

-   GitHub OAuth authentication
-   Session-based login (secure cookies)
-   Dashboard with profile metrics
-   Profile listing + filtering
-   Profile detail view
-   Natural language search
-   Account management
-   Middleware-based route protection

------------------------------------------------------------------------

## Environment Variables

Create a `.env` file:

    DJANGO_SECRET_KEY=your_secret_key
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1
    API_BASE_URL=http://localhost:8000

------------------------------------------------------------------------

## Installation

### 1. Clone repo

    git clone <repo-url>
    cd insighta-web

### 2. Create virtual environment

    python -m venv venv
    venv\Scripts\activate

### 3. Install dependencies

    pip install -r requirements.txt

------------------------------------------------------------------------

## Running the Server

    python manage.py migrate
    python manage.py runserver

Visit:

    http://127.0.0.1:8000/login

------------------------------------------------------------------------

## Authentication Flow

1.  User clicks "Continue with GitHub"
2.  Redirects to backend OAuth endpoint
3.  Backend authenticates user
4.  Redirects back with tokens
5.  Tokens stored in session
6.  Middleware protects routes

------------------------------------------------------------------------

## Middleware

`WebAuthMiddleware` ensures: - Unauthenticated users are redirected to
`/login` - Protected routes require session token

------------------------------------------------------------------------

## API Communication

All API calls: - Use `httpx` - Include Bearer token - Support automatic
token refresh

------------------------------------------------------------------------

## CI Pipeline

GitHub Actions: - Runs on pull requests - Installs dependencies - Lints
with flake8 - Runs Django system checks

------------------------------------------------------------------------

## Security Notes

-   `.env` is required (never commit it)
-   Session cookies are:
    -   HttpOnly
    -   Secure (in production)
    -   SameSite=Lax

------------------------------------------------------------------------

## Production Notes

-   Set `DEBUG=False`
-   Use HTTPS
-   Configure proper `ALLOWED_HOSTS`
-   Store secrets securely (Railway, etc.)

------------------------------------------------------------------------

## Next Improvements

-   Pagination UI improvements
-   Better error handling
-   Role-based access control
-   API caching
-   UI polish

------------------------------------------------------------------------

## Summary

This project represents a **production-style Django frontend** that: -
cleanly separates UI from backend - handles authentication securely -
interacts with APIs like a real system
