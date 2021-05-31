import uuid
from datetime import datetime
from typing import Optional

from odmantic import Model


class Movie(Model):
    uid: Optional[str]
    name: str
    imdb_score: float
    genre: list
    director: str
    popularity: float
    created_at: Optional[datetime]   # Dynamic Default value  - not supported yet
    modified_at: Optional[datetime]  # Dynamic Default value  - not supported yet


class Genre(Model):
    uid: Optional[str]
    name: str
    created_at: Optional[datetime]   # Dynamic Default value  - not supported yet
    modified_at: Optional[datetime]  # Dynamic Default value  - not supported yet


class Director(Model):
    uid: Optional[str]
    name: str
    created_at: Optional[datetime]   # Dynamic Default value  - not supported yet
    modified_at: Optional[datetime]  # Dynamic Default value  - not supported yet
