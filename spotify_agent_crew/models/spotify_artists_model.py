from pydantic import BaseModel
from typing import List


class SpotifyArtistsModel(BaseModel):
    """Structured output model listing artist names.

    Intended as the JSON schema for tasks that analyze a prompt into artists.
    """

    artists: List[str]
