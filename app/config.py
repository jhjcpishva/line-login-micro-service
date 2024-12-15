import os
from os.path import join, dirname
from dotenv import load_dotenv


load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), os.getenv("DOTENV", '.env'))
load_dotenv(dotenv_path)

APP_TITLE = os.getenv("APP_TITLE")

LINE_CHANNEL_ID = os.getenv("LINE_CHANNEL_ID")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

APP_PORT = int(os.getenv("APP_PORT", "8000"))
APP_ALLOW_ORIGINS = os.getenv("APP_ALLOW_ORIGINS", "*")
APP_PAGE_CONTEXT_PATH = os.getenv("APP_PAGE_CONTEXT_PATH", "")
APP_API_CONTEXT_PATH = os.getenv("APP_API_CONTEXT_PATH", "/api")

PRODUCTION = os.getenv("PRODUCTION", "False").lower() == 'true'

SQLITE_FILE = os.getenv("SQLITE_FILE", ":memory:")