import asyncio

import pymongo
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from odmantic import AIOEngine

from app.config import Config
from app.db import MONGO_CLIENT, DB_MOTOR_ENGINE

# from app.exceptions.routers import register_exception_handlers
from app.main import ROUTER as main_router
from app.auth import ROUTER as auth_router


def create_app(config: Config=None):
    app = FastAPI(debug=config.DEBUG if config else False)
    app.include_router(main_router)
    app.include_router(auth_router)
    if config:
        global DB_ENGINE
        DB_ENGINE = AIOEngine(database=config.TEST_DB_NAME if config.IS_TESTING else config.MONGODB_DB_NAME)

    return app

