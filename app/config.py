import os

from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env", override=True)


class Config:
    MONGODB_HOST = "localhost"
    MONGODB_PORT = 27017
    MONGODB_URI = "mongodb://localhost:27017"

    MONGODB_DB_NAME = "imdb"

    ASSESTS_PATH = "app/static/assets"
    FILEUPLOAD_DIR = "app/static/assets/img"
    TEMPLATES_PATH = "app/templates"

    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    SECRET_KEY = os.getenv("SECRET_KEY")

    TEST_DB_HOST = "localhost"
    TEST_DB_PORT = 27017
    TEST_DB_NAME = "test"

    def __init__(self, is_testing=False, debug=False):
        self.IS_TESTING = is_testing
        self.DEBUG = debug
