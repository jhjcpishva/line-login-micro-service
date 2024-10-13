import os
from os.path import join, dirname
from dotenv import load_dotenv


load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), os.getenv("DOTENV", '.env'))
load_dotenv(dotenv_path)

APP_TITLE = os.getenv("APP_TITLE")

LINE_CHANNEL_ID = os.getenv("LINE_CHANNEL_ID")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

PORT = int(os.getenv("PORT", "8000"))
ENDPOINT_LOGIN = os.getenv("ENDPOINT_LOGIN", "/login")
ENDPOINT_AUTH = os.getenv("ENDPOINT_AUTH", "/auth")

PRODUCTION = os.getenv("PRODUCTION", "False").lower() == 'true'

