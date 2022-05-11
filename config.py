import os
import logging

logger = logging.getLogger(__name__)

class Config(object):
    # Config in .env file
    TOKEN = os.getenv("TOKEN")