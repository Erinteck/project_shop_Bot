import os

class Config(object):
    APP_ID = int(os.environ.get("APP_ID", 'your APP_ID'))
    API_HASH = os.environ.get("API_HASH", "API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "BOT_TOKEN")
