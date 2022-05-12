from os import environ
import logging
import decimal

decimals = decimal.Context()
decimals.prec = 18

logger = logging.getLogger(__name__)

class Config(object):
    DATABASE_URL = environ.get("DATABASE_URL")
    RABBITMQ_URL = environ.get("RABBITMQ_URL")

    BSC_NODE_URL = environ.get("BSC_NODE_URL")
    BSC_ADMIN_ADDRESS = environ.get("BSC_ADMIN_ADDRESS")

    DUST_MULTIPLICATOR = decimals.create_decimal(environ.get('DUST_MULTIPLICATOR', '2.0'))