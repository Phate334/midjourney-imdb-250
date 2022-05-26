from datetime import datetime
from typing import List

from pydantic import BaseModel


class Movie(BaseModel):
    rank: int
    title: str = ""
    title_tw: str
    presentation: str = ""
    url: str = ""


class TopMovies(BaseModel):
    movies: List[Movie] = []
    url: str
    last_update: datetime = None
