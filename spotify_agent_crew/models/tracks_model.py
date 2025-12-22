from pydantic import BaseModel
from typing import List


class TracksModel(BaseModel):
    uris: List[str]
