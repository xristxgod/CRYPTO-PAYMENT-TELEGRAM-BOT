import sys
import asyncio
import argparse
from config import logger
from src.external.db import DB
from src.services.to_main_wallet_native import send_to_main_wallet_native

def create_parser():
    """:return: Getting script params"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", default=None)
    parser.add_argument("-l", "--limit", default=None)
    return parser

async def initial_for_address(address: str, token: str, limit):
    if token in ['bsc', None]:
        await send_to_main_wallet_native(address, limit=limit)

async def async_run(address, limit):
    if address is None:
        addresses = await DB.get_wallets()
    else:
        addresses = [address]

    for _address in addresses:
        logger.error(f'ADDRESS: {_address}')
        await initial_for_address(_address, 'bsc', limit)

if __name__ == "__main__":
    namespace = create_parser().parse_args(sys.argv[1:])
    asyncio.run(async_run(
        address=namespace.address,
        limit=namespace.limit
    ))