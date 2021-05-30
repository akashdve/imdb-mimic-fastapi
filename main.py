import time

import uvicorn
from app import create_app


if __name__ == '__main__':
    uvicorn.run(create_app(), host="0.0.0.0")

#
# from typing import List
#
# from fastapi import FastAPI, HTTPException
# from motor.motor_asyncio import AsyncIOMotorClient
#
# from odmantic import AIOEngine, Model, ObjectId
#
#
# class Tree(Model):
#     name: str
#     average_size: float
#     discovery_year: int
#
#
# app = FastAPI()
#
# MONGO_CLIENT = AsyncIOMotorClient("localhost", 27017)
#
#
#
# @app.get("/trees/", response_model=Tree)
# async def create_tree(tree: Tree):
#     start = time.time()
#     engine = AIOEngine(motor_client=MONGO_CLIENT)
#     await engine.save(tree)
#     print(f"Time taken  {time.time()-start} seconds")
#     return tree
#
# if __name__ == '__main__':
#     uvicorn.run(app)