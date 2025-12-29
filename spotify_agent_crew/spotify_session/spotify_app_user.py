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
        if cls._instance is None:
            cls(user_json)
        else:
            cls._instance.id = user_json.get("id", cls._instance.id)
            cls._instance.display_name = user_json.get("display_name", cls._instance.display_name)
            cls._instance.country = user_json.get("country", cls._instance.country)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("SpotifyAppUser not initialized")
        return cls._instance

    @classmethod
    def get_id(cls) -> str:
        return cls.get_instance().id

    @classmethod
    def get_display_name(cls) -> str:
        return cls.get_instance().display_name

    @classmethod
    def get_country(cls) -> str:
        return cls.get_instance().country