from os import environ
import decimal
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

decimals = decimal.Context()
decimals.prec = 18

class Config(object):
    NETWORK = bool(int(environ.get('NETWORK', 0)))

    DATABASE_URL = environ.get("DATABASE_URL")
    RABBITMQ_URL = environ.get("RABBITMQ_URL")
    REDIS_URL = environ.get("REDIS_URL")

    TOKEN = environ.get("TOKEN")
    ADMIN_IDS = [int(x) for x in environ.get('ADMIN_IDS').split(',')]

    TRON_NODE_URL = environ.get("TRON_NODE_URL")
    TRON_ADMIN_ADDRESS = environ.get("TRON_ADMIN_ADDRESS")
    TRON_ADMIN_PRIVATE_KEY = environ.get("TRON_ADMIN_PRIVATE_KEY")
    TRON_WITHDRAW_ADMIN_ADDRESS = environ.get('TRON_WITHDRAW_ADMIN_ADDRESS')
    TRON_WITHDRAW_ADMIN_PRIVATE_KEY = environ.get('TRON_WITHDRAW_ADMIN_PRIVATE_KEY')

    BSC_NODE_URL = environ.get("BSC_NODE_URL")
    BSC_ADMIN_ADDRESS = environ.get("BSC_ADMIN_ADDRESS")
    BSC_ADMIN_PRIVATE_KEY = environ.get("BSC_ADMIN_PRIVATE_KEY")
    BSC_WITHDRAW_ADMIN_ADDRESS = environ.get('BSC_WITHDRAW_ADMIN_ADDRESS')
    BSC_WITHDRAW_ADMIN_PRIVATE_KEY = environ.get('BSC_WITHDRAW_ADMIN_PRIVATE_KEY')
