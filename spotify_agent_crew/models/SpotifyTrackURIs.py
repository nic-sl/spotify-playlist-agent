from pydantic import BaseModel
from typing import List

class SpotifyTrackURIs(BaseModel):
    uris: List[str]
