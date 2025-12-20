from pydantic import BaseModel
from typing import List

class SpotifyArtistsModel(BaseModel):
    artists: List[str]
