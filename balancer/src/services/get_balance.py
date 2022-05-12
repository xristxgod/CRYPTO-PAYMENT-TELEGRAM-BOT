import decimal

from src.services.node import node_singleton
from config import decimals

async def get_balance(address: str) -> decimal.Decimal:
    try:
        address = node_singleton.async_node.toChecksumAddress(address)
        balance: decimal.Decimal = node_singleton.async_node.fromWei(
            node_singleton.node.eth.get_balance(address), "ether"
        )
        return decimals.create_decimal(balance)
    except:
        return None