# Insighta Web Portal

## Overview

This repository contains the **Insighta Web Portal**, a Django-based
frontend that connects to the Insighta backend API.

-   Built with **Django templates**
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

-   GitHub OAuth authentication\
-   Session-based login (secure cookies)\
-   Dashboard with profile metrics\
-   Profile listing + filtering\
-   Profile detail view\
-   Natural language search\
-   Account management\
-   Middleware-based route protection

------------------------------------------------------------------------

## Routes Documentation

### Public Routes

  Route            Method   Description
  ---------------- -------- --------------------------
  /login           GET      Login page
  /auth/github     GET      Redirect to GitHub OAuth
  /auth/callback   GET      OAuth callback handler

------------------------------------------------------------------------

### Protected Routes (Require Session)

  Route                     Method   Description
  ------------------------- -------- ----------------------------
  /dashboard                GET      Dashboard overview
  /profiles                 GET      List profiles with filters
  /profiles/`<id>`{=html}   GET      View profile details
  /search                   GET      Search profiles
  /account                  GET      User account page
  /logout                   GET      Logout user

------------------------------------------------------------------------

## Query Parameters

### `/profiles`

-   `page` (default: 1)\
-   `limit` (default: 10)\
-   `gender`\
-   `country`\
-   `age_group`

### `/search`

-   `q` → natural language query

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

1.  User visits `/login`\
2.  Clicks "Continue with GitHub"\
3.  Redirects to `/auth/github`\
4.  Backend handles OAuth\
5.  Redirects to `/auth/callback` with tokens\
6.  Tokens stored in session\
7.  Middleware enforces access to protected routes

------------------------------------------------------------------------

## Middleware

`WebAuthMiddleware` ensures:

-   Unauthenticated users are redirected to `/login`\
-   Protected routes require a valid session\
-   Only public routes are accessible without authentication

------------------------------------------------------------------------

## API Communication

All API calls:

-   Use `httpx`\

-   Include headers:

        Authorization: Bearer <token>
        X-API-Version: 1

-   Automatically attempt token refresh on `401 Unauthorized`

------------------------------------------------------------------------

## CI Pipeline

GitHub Actions:

-   Runs on pull requests\
-   Installs dependencies\
-   Lints with `flake8`\
-   Runs Django system checks

------------------------------------------------------------------------

## Security Notes

-   `.env` must never be committed\
-   Session cookies are:
    -   HttpOnly\
    -   Secure (in production)\
    -   SameSite=Lax

------------------------------------------------------------------------

## Production Notes

-   Set `DEBUG=False`\
-   Use HTTPS\
-   Configure proper `ALLOWED_HOSTS`\
-   Store secrets securely

------------------------------------------------------------------------

## Next Improvements

-   Pagination UI enhancements\
-   Better error handling\
-   Role-based access control\
-   API caching\
-   UI polish

------------------------------------------------------------------------

## Summary

This project represents a **production-style Django frontend** that:

-   Cleanly separates UI from backend\
-   Handles authentication securely\
-   Interacts with APIs like a real-world system
