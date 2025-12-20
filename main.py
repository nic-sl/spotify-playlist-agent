import os
import base64
import secrets
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates

import spotify_agent_crew.crew
from spotify_agent_crew.spotify_session.spotify_token_manager import SpotifyTokenManager
from spotify_agent_crew.spotify_session.spotify_app_user import SpotifyAppUser

# Load environment variables from .env if present
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8000/callback")
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-secret-change-me")

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SCOPES = "playlist-modify-private playlist-modify-public"

app = FastAPI(title="Spotify Playlist Agent")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render landing page.

    Shows a "Login with Spotify" button and indicates whether real OAuth is
    configured based on environment variables.
    """
    spotify_configured = bool(SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "spotify_configured": spotify_configured,
        },
    )

@app.get("/login")
async def login(request: Request):
    """Start the Spotify OAuth authorization flow.

    Generates and stores a CSRF `state` in the session and redirects the user
    to Spotify's authorize URL with required query parameters.
    """
    state = secrets.token_urlsafe(16)
    request.session["oauth_state"] = state
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": SPOTIFY_SCOPES,
        "state": state,
        "show_dialog": "false",
    }
    # Build the authorization URL
    qs = "&".join(f"{k}={httpx.QueryParams({k: v})[k]}" for k, v in params.items())
    return RedirectResponse(url=f"{SPOTIFY_AUTH_URL}?{qs}")

@app.get("/callback")
async def callback(request: Request, code: Optional[str] = None, state: Optional[str] = None, error: Optional[str] = None):
    """Handle the OAuth redirect from Spotify.

    Validates the CSRF `state`, exchanges the authorization code for tokens,
    optionally fetches the profile of the authenticated user, persists token
    and user info in the session and helper singletons, and redirects to /chat.
    """
    # If Spotify isn't configured, just redirect to chat
    if not (SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET):
        return RedirectResponse(url="/chat")

    if error:
        return RedirectResponse(url=f"/chat?error={error}")

    saved_state = request.session.get("oauth_state")
    if not state or state != saved_state:
        return RedirectResponse(url="/?error=state_mismatch")

    if not code:
        return RedirectResponse(url="/?error=missing_code")

    # Exchange code for token
    auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        token_resp = await client.post(SPOTIFY_TOKEN_URL, data=data, headers=headers)
        if token_resp.status_code != 200:
            return RedirectResponse(url="/?error=token_exchange_failed")
        tokens = token_resp.json()

        # Optionally fetch user profile to display name
        access_token = tokens.get("access_token")
        me = None
        if access_token:
            me_resp = await client.get(
                "https://api.spotify.com/v1/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if me_resp.status_code == 200:
                me = me_resp.json()

    request.session["tokens"] = tokens
    request.session["user"] = {
        "display_name": (me or {}).get("display_name") or (me or {}).get("id") or "Spotify User",
        "country": (me or {}).get("country"),
    }
    SpotifyTokenManager.from_json(tokens)
    SpotifyAppUser.from_json(me)
    return RedirectResponse(url="/chat")

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    """Render the chat page for an authenticated session."""
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("chat.html", {"request": request, "user": user})

@app.post("/api/create")
async def create(prompt: str = Form(...)):
    """Trigger the crew pipeline using the provided `prompt`.

    Currently delegates to `spotify_agent_crew.crew.run(prompt)`.
    """
    spotify_agent_crew.crew.run(prompt)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
