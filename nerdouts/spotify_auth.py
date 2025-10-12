"""Spotify OAuth authentication module for Web Playback SDK."""

import os
import requests
from urllib.parse import urlencode
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Spotify OAuth configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = "http://localhost:8000/callback"

# Validate that credentials are provided
if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    raise ValueError(
        "Missing Spotify credentials. Please set SPOTIFY_CLIENT_ID and "
        "SPOTIFY_CLIENT_SECRET in your .env file."
    )

router = APIRouter()


@router.get("/spotify/login")
async def spotify_login():
    """Redirect user to Spotify authorization page."""
    auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": "streaming user-read-private user-read-email",
        "show_dialog": "true"
    }
    return RedirectResponse(url=f"{auth_url}?{urlencode(params)}")


@router.get("/callback")
async def spotify_callback(code: str = None, error: str = None):
    """Handle Spotify authorization callback."""
    if error:
        return JSONResponse({"error": error}, status_code=400)

    if not code:
        return JSONResponse({"error": "No authorization code received"}, status_code=400)

    # Exchange code for access token
    token_url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET
    }

    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
    except requests.RequestException as e:
        return JSONResponse(
            {"error": f"Failed to get access token: {str(e)}"},
            status_code=500
        )

    tokens = response.json()

    if "access_token" not in tokens:
        return JSONResponse(
            {"error": "No access token in response"},
            status_code=500
        )

    # Return a page that stores the token in localStorage and redirects
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Spotify Login Complete</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h1>Login Successful!</h1>
        <p>You're now authenticated with Spotify. Redirecting...</p>
        <script>
            // Store the tokens in localStorage for the frontend to use
            localStorage.setItem('spotify_access_token', '{tokens['access_token']}');
            localStorage.setItem('spotify_refresh_token', '{tokens['refresh_token']}');
            localStorage.setItem('spotify_expires_in', '{tokens.get('expires_in', 3600)}');

            // Redirect back to home page
            window.location.href = '/';
        </script>
    </body>
    </html>
    """)


@router.get("/api/spotify/user")
async def get_spotify_user(authorization: str = Header(None)):
    """Get current Spotify user profile using access token from header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")

    try:
        response = requests.get(
            'https://api.spotify.com/v1/me',
            headers={'Authorization': authorization}
        )

        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if not response.ok:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to get user profile"
            )

        user_data = response.json()
        return {
            "id": user_data.get("id"),
            "display_name": user_data.get("display_name"),
            "email": user_data.get("email"),
            "images": user_data.get("images", [])
        }

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")
