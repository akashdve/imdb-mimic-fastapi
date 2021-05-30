import json


# def import_from_json(filepath, DB_ENGINE, Model):
import uuid
from datetime import datetime

from odmantic import AIOEngine
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

FILEPATH = "/home/akash/Downloads/imdb.json t.json"


async def import_from_file():
    DB_ENGINE = AIOEngine(database="imdb")
    with open(FILEPATH, "r") as fp:
         obj = json.load(fp)
         if isinstance(obj, list):
             # obj = [Movie(name=o.get("name"), imdb_score=o.get("imdb_score"), director=o.get("director"), popularity=o.get("99popularity"), genre=[x.strip() for x in o.get("genre")]) for o in obj]
             # await DB_ENGINE.save_all(obj)

             gset = set(); dset = set()
             for o in obj:
                 for g in o.get("genre"):
                     gset.add(g.strip())
                 dset.add(o.get("director"))

             for g in gset:
                 await DB_ENGINE.save(Genre(name=g))
             for d in dset:
                 await DB_ENGINE.save(Director(name=d))

         elif isinstance(obj, dict):
             obj = Movie(name=obj.get("name"), imdb_score=obj.get("imdb_score"), director=obj.get("director"), popularity=obj.get("99popularity"), genre=obj.get("genre"))
             await DB_ENGINE.save(obj)

