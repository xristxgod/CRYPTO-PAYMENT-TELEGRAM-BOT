from os import environ, path, listdir, mkdir
import logging
import decimal

decimals = decimal.Context()
decimals.prec = 18

ROOT_DIR = path.dirname(path.abspath(__file__))
BASE_DIR = path.join(ROOT_DIR, "files")
NOT_SEND = path.join(BASE_DIR, 'not_send')
LAST_BLOCK = path.join(BASE_DIR, "last_block.txt")
# Errors Recording
ERROR = path.join(BASE_DIR, "error.txt")

if "files" not in listdir(ROOT_DIR): mkdir(BASE_DIR)
if 'not_send' not in listdir(BASE_DIR): mkdir(NOT_SEND)

if "last_block.txt" not in listdir(BASE_DIR):
    with open(LAST_BLOCK, "w") as file:
        file.write("")

logger = logging.getLogger(__name__)

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
    TRON_WITHDRAW_ADMIN_ADDRESS = environ.get('TRON_WITHDRAW_ADMIN_ADDRESS', '')
    TRON_WITHDRAW_ADMIN_PRIVATE_KEY = environ.get('TRON_WITHDRAW_ADMIN_PRIVATE_KEY', '')
    TRON_WALLET_FEE_DEFAULT = environ.get('TRON_WALLET_FEE_DEFAULT')

    BSC_NODE_URL = environ.get("BSC_NODE_URL")
    BSC_ADMIN_ADDRESS = environ.get("BSC_ADMIN_ADDRESS")
    BSC_ADMIN_PRIVATE_KEY = environ.get("BSC_ADMIN_PRIVATE_KEY")
    BSC_WITHDRAW_ADMIN_ADDRESS = environ.get('BSC_WITHDRAW_ADMIN_ADDRESS')
    BSC_WITHDRAW_ADMIN_PRIVATE_KEY = environ.get('BSC_WITHDRAW_ADMIN_PRIVATE_KEY')
    BSC_WALLET_FEE_DEFAULT = environ.get('BSC_WALLET_FEE_DEFAULT')