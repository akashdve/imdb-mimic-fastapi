import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from app.config import Config

MONGO_CLIENT = AsyncIOMotorClient(Config.MONGODB_HOST, Config.MONGODB_PORT)


DB_MOTOR_ENGINE = MONGO_CLIENT[Config.MONGODB_DB_NAME]

DB_ENGINE = AIOEngine(motor_client=MONGO_CLIENT, database=Config.MONGODB_DB_NAME)
