"""Singleton that stores the current Spotify user's basic profile.

The instance is populated from the Spotify `me` endpoint JSON and provides
simple accessors for id, display name, and country.
"""

class SpotifyAppUser:
    _instance = None

    def __init__(self, user_json: dict):
        if SpotifyAppUser._instance is not None:
            raise RuntimeError("Use SpotifyAppUser.get_instance() instead of creating directly")

        self.id = user_json.get("id")
        self.display_name = user_json.get("display_name") or self.id or "Spotify User"
        self.country = user_json.get("country")

        SpotifyAppUser._instance = self

    @classmethod
    def from_json(cls, user_json: dict):
        """Initialize or update the singleton from a Spotify user JSON dict.

        The dict typically comes from `GET https://api.spotify.com/v1/me`.
        """
        if cls._instance is None:
            cls(user_json)
        else:
            # Optionally update the existing instance
            cls._instance.id = user_json.get("id", cls._instance.id)
            cls._instance.display_name = user_json.get("display_name", cls._instance.display_name)
            cls._instance.country = user_json.get("country", cls._instance.country)

    @classmethod
    def get_instance(cls):
        """Retrieve the initialized singleton instance.

        Raises:
            RuntimeError: If `from_json` has not been called yet.
        """
        if cls._instance is None:
            raise RuntimeError("SpotifyAppUser not initialized")
        return cls._instance

    @classmethod
    def get_id(cls) -> str:
        """Return the Spotify user id for the current session."""
        return cls.get_instance().id

    @classmethod
    def get_display_name(cls) -> str:
        """Return a display name for the user (falls back to id or default)."""
        return cls.get_instance().display_name

    @classmethod
    def get_country(cls) -> str:
        """Return the user's two-letter country code, if available."""
        return cls.get_instance().country