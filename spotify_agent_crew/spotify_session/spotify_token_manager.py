"""Token management for Spotify Web API access.

Provides a simple class that stores and refreshes access tokens for both user
and client-credential contexts. The manager can be initialized from a token
JSON and will refresh tokens when expired.
"""

import time
import requests
import os

class SpotifyTokenManager:
    """Simple in-memory token holder and refresher for Spotify API.

    This class is intentionally minimal and not thread-safe. In a production
    setting, consider persisting tokens securely and coordinating refreshes.
    """
    _token = None
    _expires_at = 0
    _refresh_token = None

    AUTH_URL = "https://accounts.spotify.com/api/token"

    @classmethod
    def from_json(cls, tokens: dict):
        """Initialize the manager from Spotify token JSON.

        Expected keys include `access_token`, `expires_in`, and optionally
        `refresh_token`.
        """
        access_token = tokens.get("access_token")
        expires_in = tokens.get("expires_in", 3600)
        refresh_token = tokens.get("refresh_token")

        if not access_token:
            raise ValueError("Missing access_token in token JSON")

        cls._token = access_token
        cls._expires_at = time.time() + expires_in - 30  # buffer
        cls._refresh_token = refresh_token

    @classmethod
    def get_token(cls) -> str:
        """Return a valid access token, refreshing if needed."""
        if cls._token is None or time.time() >= cls._expires_at:
            cls._refresh_access_token()
        return cls._token

    @classmethod
    def _refresh_access_token(cls):
        """Refresh the token via refresh_token or client credentials.

        If a `refresh_token` is available, attempts the refresh grant. As a
        fallback, requests a new app token via client credentials.
        """
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

        if cls._refresh_token:
            response = requests.post(
                cls.AUTH_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": cls._refresh_token,
                },
                auth=(client_id, client_secret),
            )
        else:
            response = requests.post(
                cls.AUTH_URL,
                data={"grant_type": "client_credentials"},
                auth=(client_id, client_secret),
            )

        if response.status_code != 200:
            raise RuntimeError(f"Failed to refresh token: {response.text}")

        data = response.json()
        cls.from_json(data)
