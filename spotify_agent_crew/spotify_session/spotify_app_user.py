class SpotifyAppUser:
    _instance = None

    def __init__(self, user_json: dict):
        if SpotifyAppUser._instance is not None:
            raise Exception("Use SpotifyAppUser.get_instance() instead of creating directly")

        self.id = user_json.get("id")
        self.display_name = user_json.get("display_name") or self.id or "Spotify User"
        self.mock = user_json.get("mock", False)

        SpotifyAppUser._instance = self

    @classmethod
    def from_json(cls, user_json: dict):
        """
        Initialize the singleton from a user JSON dict.
        """
        if cls._instance is None:
            cls(user_json)
        else:
            # Optionally update existing instance
            cls._instance.id = user_json.get("id", cls._instance.id)
            cls._instance.display_name = user_json.get("display_name", cls._instance.display_name)
            cls._instance.mock = user_json.get("mock", cls._instance.mock)

    @classmethod
    def get_instance(cls):
        """
        Retrieve the singleton instance.
        """
        if cls._instance is None:
            raise Exception("SpotifyAppUser not initialized")
        return cls._instance

    @classmethod
    def get_id(cls) -> str:
        return cls.get_instance().id

    @classmethod
    def get_display_name(cls) -> str:
        return cls.get_instance().display_name

    @classmethod
    def is_mock(cls) -> bool:
        return cls.get_instance().mock
