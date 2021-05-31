import os
import random
import re
import uuid
from datetime import datetime
from sqlite3 import IntegrityError
from typing import List, Optional

import pymongo
from fastapi import Request, Form, UploadFile, File, Depends, HTTPException
from fastapi import APIRouter
from fastapi import status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient

from slugify import slugify

from app.auth.utils import get_current_active_user
from app.db import MONGO_CLIENT, DB_ENGINE
# from app.exceptions.routers import error_page
from app.models.user import User, AuthUser
from app.models.movie import Movie, Director, Genre

from app.config import Config

main_router = APIRouter()


@main_router.on_event("startup")
def startup():
    DB_MOTOR_ENGINE = MONGO_CLIENT[Config.MONGODB_DB_NAME]
    DB_MOTOR_ENGINE.movie.create_index([("name", pymongo.TEXT), ("director", pymongo.TEXT)])


@main_router.on_event("shutdown")
def shutdown():
    pass


@main_router.get("/")
async def index(current_user: AuthUser = Depends(get_current_active_user)):
    if current_user.is_authenticated:
        return f"Welcome to IMDB-mimic, {current_user.username} !"
    else:
        return f"Welcome to IMDB-mimic !!"


@main_router.get("/movies")
async def list_movies(request: Request):
    """
    List all movies sorted based on popularity and filtered by keyword if given
    Also accepts "size" and "page" query params for pagination
    :param request:
    :return: list of movies
    """
    keyword = request.query_params.get("keyword", "")
    size = request.query_params.get("size", 10)
    page = request.query_params.get("page", 1)

    try:
        size = int(size)
        page = int(page)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if keyword:
        keyword = re.compile(keyword, re.IGNORECASE)
        movies = await DB_ENGINE.find(Movie,
                                      Movie.name.match(keyword),
                                      sort=Movie.popularity.desc(),
                                      skip=(page-1)*size,
                                      limit=size)
    else:
        movies = await DB_ENGINE.find(Movie,
                                      sort=Movie.popularity.desc(),
                                      skip=(page-1)*size,
                                      limit=size)

    resp = {
        "data": movies,
        "size": size,
        "page": page
    }
    return resp


@main_router.get("/movies/{movie_id}", response_model=Movie)
async def get_movie_by_id(movie_id):
    try:
        movie_obj = await DB_ENGINE.find_one(Movie, Movie.uid == movie_id)
        if movie_obj:
            return movie_obj
        else:
            raise
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cannot find movie with ID - {movie_id}")



@main_router.post("/movies")
async def add_movies(new_movies: List[Movie], current_user: User = Depends(get_current_active_user)):
    if not isinstance(new_movies, list):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    try:
        for movie in new_movies:
            if not movie.uid: movie.uid = str(uuid.uuid4())
            if not movie.created_at:
                movie.created_at = datetime.utcnow()
                movie.modified_at = datetime.utcnow()
        await DB_ENGINE.save_all(new_movies)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return new_movies


@main_router.put("/movies/{movie_id}")
async def update_movie(movie_id, updated_movie: Movie, current_user: User = Depends(get_current_active_user)):
    """
    Update movie object based on movie id
    :param movie_id: UUID
    :param updated_movie: updated object of Movie
    :param current_user: Dependency Injection
    :return:
    """
    try:
        movie_obj = await DB_ENGINE.find_one(Movie, Movie.uid == movie_id)
        if movie_obj is None: raise
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cannot find movie with Id {movie_id}")
    movie_obj.name=updated_movie.name
    movie_obj.imdb_score=updated_movie.imdb_score
    movie_obj.genre = updated_movie.genre
    movie_obj.director = updated_movie.director
    movie_obj.popularity = updated_movie.popularity
    movie_obj.modified_at = datetime.utcnow()
    await DB_ENGINE.save(movie_obj)
    return movie_id


@main_router.delete("/movies/{movie_id}", response_model=Movie)
async def delete_movie(movie_id, current_user: User = Depends(get_current_active_user)):
    """
    Delete movie object based on movie id
    :param movie_id: UUID
    :param current_user: Dependency Injection
    :return:
    """
    try:
        movie_obj = await DB_ENGINE.find_one(Movie, Movie.uid == movie_id)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cannot find movie with id {movie_id}")

    await DB_ENGINE.delete(movie_obj)
    return movie_obj


@main_router.get("/search")
async def search_movies(request: Request):
    """
    Advanced search for movies sorted based on popularity and filtered by keyword if given
    Also accepts "size" and "page" query params for pagination
    :param request:
    :return: list of movies
    """
    keyword = request.query_params.get("keyword", "")
    genres = request.query_params.get("genres", "")
    min_rating = request.query_params.get("min_rating", 0.0)
    max_rating = request.query_params.get("max_rating", 10.0)
    phrase_match = request.query_params.get("phrase_match")
    size = request.query_params.get("size", 10)
    page = request.query_params.get("page", 1)

    try:
        size = int(size)
        page = int(page)
        genres = [genre for genre in genres.split(",") if genre.strip()]
        min_rating = float(min_rating)
        max_rating = float(max_rating)
        if phrase_match:
            if phrase_match == "true":
                phrase_match = True
            else:
                phrase_match = False
        else:
            phrase_match = False
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if phrase_match:
        keyword = re.compile(keyword, re.IGNORECASE)
    else:
        # # Regex: (?:word1) | (?:word2) | (?:word3)
        keyword = re.compile("|".join([f"(?:{x})" for x in keyword.split() if x.strip()]), re.IGNORECASE)
        print(keyword)

    queries = [
        Movie.name.match(keyword) if keyword else None,
        Movie.genre.in_(genres) if len(genres) > 0 else None,
        Movie.imdb_score.gte(min_rating),
        Movie.imdb_score.lte(max_rating)
    ]

    queries = [q for q in queries if q is not None]
    print(queries)

    movies = await DB_ENGINE.find(Movie,
                                  *queries,
                                  sort=Movie.popularity.desc(),
                                  skip=(page-1)*size,
                                  limit=size)

    count = await DB_ENGINE.count(Movie,
                                  *queries)

    resp = {
        "data": movies,
        "count": count,
        "size": size,
        "page": page
    }
    return resp



@main_router.get("/genres")
async def list_genres(request: Request):
    """
    List all genres sorted chronologically and filtered by keyword if given
    Also accepts "size" and "page" query params for pagination
    :param request:
    :return: list of genres
    """
    keyword = request.query_params.get("keyword", "")
    size = request.query_params.get("size", 10)
    page = request.query_params.get("page", 1)

    try:
        size = int(size)
        page = int(page)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if keyword:
        keyword = re.compile(keyword, re.IGNORECASE)
        genres = await DB_ENGINE.find(Genre,
                                      Genre.name.match(keyword),
                                      sort=Genre.name,
                                      skip=(page-1)*size,
                                      limit=size)
    else:
        genres = await DB_ENGINE.find(Genre,
                                      sort=Genre.name,
                                      skip=(page-1)*size,
                                      limit=size)

    resp = {
        "data": genres,
        "size": size,
        "page": page
    }
    return resp


@main_router.post("/genres")
async def add_genres(new_genres: List[Genre], current_user: User = Depends(get_current_active_user)):
    if not isinstance(new_genres, list):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    try:
        for genre in new_genres:
            if not genre.uid: genre.uid = str(uuid.uuid4())
            if not genre.created_at:
                genre.created_at = datetime.utcnow()
                genre.modified_at = datetime.utcnow()
        await DB_ENGINE.save_all(new_genres)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return new_genres


@main_router.put("/genres/{genre_id}")
async def update_genre(genre_id, updated_genre: Genre, current_user: User = Depends(get_current_active_user)):
    """
    Update genre object based on genre id
    :param genre_id: UUID
    :param updated_genre: updated object of Genre
    :param current_user: Dependency Injection
    :return:
    """
    try:
        genre_obj = await DB_ENGINE.find_one(Genre, Genre.uid == genre_id)
        if genre_obj is None: raise
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cannot find genre with ID - {genre_id}")
    genre_obj.name = updated_genre.name
    genre_obj.modified_at = datetime.utcnow()
    await DB_ENGINE.save(genre_obj)
    return genre_obj.uid


@main_router.delete("/genres/{genre_id}", response_model=Genre)
async def delete_genre(genre_id, current_user: User = Depends(get_current_active_user)):
    """
    Delete genre object based on genre id
    :param genre_id: UUID
    :param current_user: Dependency Injection
    :return:
    """
    try:
        genre_obj = await DB_ENGINE.find_one(Genre, Genre.uid == genre_id)
        if genre_obj is None: raise
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cannot find genre with ID - {genre_id}")
    await DB_ENGINE.delete(genre_obj)
    return genre_obj




@main_router.get("/directors")
async def list_directors(request: Request):
    """
    List all directors sorted chronologically and filtered by keyword if given
    Also accepts "size" and "page" query params for pagination
    :param request:
    :return: list of directors
    """
    keyword = request.query_params.get("keyword", "")
    size = request.query_params.get("size", 10)
    page = request.query_params.get("page", 1)

    try:
        size = int(size)
        page = int(page)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if keyword:
        keyword = re.compile(keyword, re.IGNORECASE)
        directors = await DB_ENGINE.find(Director,
                                      Director.name.match(keyword),
                                      sort=Director.name,
                                      skip=(page-1)*size,
                                      limit=size)
    else:
        directors = await DB_ENGINE.find(Director,
                                      sort=Director.name,
                                      skip=(page-1)*size,
                                      limit=size)

    resp = {
        "data": directors,
        "size": size,
        "page": page
    }
    return resp

@main_router.post("/directors")
async def add_directors(new_directors: List[Director], current_user: User = Depends(get_current_active_user)):
    if not isinstance(new_directors, list):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    try:
        for director in new_directors:
            if not director.uid: director.uid = str(uuid.uuid4())
            if not director.created_at:
                director.created_at = datetime.utcnow()
                director.modified_at = datetime.utcnow()

        await DB_ENGINE.save_all(new_directors)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return new_directors


@main_router.put("/directors/{director_id}")
async def update_director(director_id, updated_director: Director, current_user: User = Depends(get_current_active_user)):
    """
    Update director object based on director id
    :param genre_id: UUID
    :param updated_genre: updated object of Director
    :param current_user: Dependency Injection
    :return:
    """
    try:
        director_obj = await DB_ENGINE.find_one(Director, Director.uid == director_id)
        if director_obj is None: raise
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cannot find director with ID - {director_id}")
    director_obj.name = updated_director.name
    director_obj.modified_at = datetime.utcnow()
    await DB_ENGINE.save(director_obj)
    return director_obj.uid


@main_router.delete("/directors/{director_id}", response_model=Director)
async def delete_director(director_id, current_user: User = Depends(get_current_active_user)):
    """
    Delete director object based on director id
    :param director_id: UUID
    :param current_user: Dependency Injection
    :return:
    """
    try:
        director_obj = await DB_ENGINE.find_one(Director, Director.uid == director_id)
        if director_obj is None: raise
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cannot find director with ID - {director_id}")
    await DB_ENGINE.delete(director_obj)
    return director_obj
