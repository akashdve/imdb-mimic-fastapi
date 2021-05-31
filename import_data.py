import json


# def import_from_json(filepath, DB_ENGINE, Model):
import uuid
from datetime import datetime
from typing import Optional

from odmantic import AIOEngine
from odmantic import Model


class Movie(Model):
    uid: Optional[str]
    name: str
    imdb_score: float
    genre: list
    director: str
    popularity: float
    created_at: Optional[datetime]
    modified_at: Optional[datetime]

class Genre(Model):
    uid: Optional[str]
    name: str
    created_at: Optional[datetime]
    modified_at: Optional[datetime]


class Director(Model):
    uid: Optional[str]
    name: str
    created_at: Optional[datetime]
    modified_at: Optional[datetime]

FILEPATH = "/home/akash/Downloads/imdb.json t.json"


async def import_from_file():
    DB_ENGINE = AIOEngine(database="imdb")
    with open(FILEPATH, "r") as fp:
         obj = json.load(fp)
         if isinstance(obj, list):
             obj = [Movie(uid=str(uuid.uuid4()),
                          name=o.get("name"),
                          imdb_score=o.get("imdb_score"),
                          director=o.get("director"),
                          popularity=o.get("99popularity"),
                          genre=[x.strip() for x in o.get("genre")],
                          created_at=datetime.utcnow(),
                          modified_at = datetime.utcnow()) for o in obj]
             await DB_ENGINE.save_all(obj)

             gset = set(); dset = set()
             for o in obj:
                 for g in o.genre:
                     gset.add(g.strip())
                 dset.add(o.director)

             for g in gset:
                 await DB_ENGINE.save(Genre(uid=str(uuid.uuid4()),
                                            name=g,
                                            created_at=datetime.utcnow(),
                                            modified_at=datetime.utcnow()
                                            ))
             for d in dset:
                 await DB_ENGINE.save(Director(uid=str(uuid.uuid4()), name=d, created_at=datetime.utcnow(), modified_at=datetime.utcnow()))

         elif isinstance(obj, dict):
             obj = Movie(uid=str(uuid.uuid4()), name=obj.get("name"), imdb_score=obj.get("imdb_score"), director=obj.get("director"), popularity=obj.get("99popularity"), genre=obj.get("genre"))
             await DB_ENGINE.save(obj)


if __name__ == '__main__':
    import asyncio
    asyncio.run(import_from_file())