from pydantic import BaseModel
from typing import List


class TracksModel(BaseModel):
    """Structured output model containing Spotify track URIs.

    Intended as the JSON schema for tasks that select tracks.
    """

    uris: List[str]
