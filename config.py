import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config(object):
    # Config in .env file
    TOKEN = os.getenv("TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")