from fastapi.testclient import TestClient

from app import create_app

client = TestClient(create_app())


class TestIndexRoute:

    pass