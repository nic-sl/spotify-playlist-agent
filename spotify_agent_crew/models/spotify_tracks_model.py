from pydantic import BaseModel
from typing import List

class SpotifyTracksModel(BaseModel):
    uris: List[str]
