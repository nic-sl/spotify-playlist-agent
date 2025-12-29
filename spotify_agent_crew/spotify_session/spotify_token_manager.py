import os
import time

from typing import Optional, Dict
from spotipy.oauth2 import SpotifyOAuth


class SpotifyTokenManager:
    _token_info: Optional[Dict] = None
    _auth_manager: Optional[SpotifyOAuth] = None

    @classmethod
    def _build_auth_manager(cls) -> SpotifyOAuth:
        if cls._auth_manager is not None:
            return cls._auth_manager

        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8000/callback")
        scope = os.getenv("SPOTIFY_SCOPES", "playlist-modify-private playlist-modify-public")

        if not client_id or not client_secret:
            raise ValueError("Spotify client credentials not set in environment variables.")

        cls._auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            cache_handler=None,
            open_browser=False,
        )
        return cls._auth_manager

    @classmethod
    def from_token_info(cls, token_info: Dict):
        if not token_info or not token_info.get("access_token"):
            raise ValueError("Invalid token_info: missing access_token")

        # Ensure expires_at exists
        if "expires_at" not in token_info:
            expires_in = int(token_info.get("expires_in", 3600))
            token_info["expires_at"] = int(time.time()) + expires_in

        cls._token_info = token_info
        cls._build_auth_manager()

    from_json = from_token_info

    @classmethod
    def get_token(cls) -> str:
        if cls._token_info is None:
            raise RuntimeError("SpotifyTokenManager not initialized with token_info")

        now = int(time.time())
        if int(cls._token_info.get("expires_at", 0)) - 30 <= now:
            cls._refresh_access_token()
        return cls._token_info["access_token"]

    @classmethod
    def _refresh_access_token(cls):
        token_info = cls._token_info or {}
        refresh_token = token_info.get("refresh_token")
        if not refresh_token:
            raise RuntimeError("No refresh_token available to refresh Spotify access token")

        auth = cls._build_auth_manager()
        new_info = auth.refresh_access_token(refresh_token)

        if "refresh_token" not in new_info and refresh_token:
            new_info["refresh_token"] = refresh_token
        cls.from_token_info(new_info)
