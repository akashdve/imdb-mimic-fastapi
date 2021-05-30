import uuid
from datetime import datetime

from odmantic import Model


class Movie(Model):
    uid: str = str(uuid.uuid4())
    name: str
    imdb_score: float
    genre: list
    director: str
    popularity: float
    created_at: datetime = datetime.utcnow()
    modified_at: datetime = datetime.utcnow()


class Genre(Model):
    uid: str = str(uuid.uuid4())
    name: str
    created_at: datetime = datetime.utcnow()
    modified_at: datetime = datetime.utcnow()


class Director(Model):
    uid: str = str(uuid.uuid4())
    name: str
    created_at: datetime = datetime.utcnow()
    modified_at: datetime = datetime.utcnow()