from pydantic import BaseModel
from typing import List


class ArtistsModel(BaseModel):
    artists: List[str]
