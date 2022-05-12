from config import decimals
from src.services.node import node_singleton

async def get_optimal_gas(from_address: str, to_address: str, amount):
    try:
        from_: str = node_singleton.async_node.toChecksumAddress(from_address)
        to_: str = node_singleton.async_node.toChecksumAddress(to_address)
    except:
        return None
    amount = "%d" % node_singleton.async_node.toWei(amount, "gwei")
    trx = {"from": from_, "to": to_, "value": amount}
    estimate_gas: int = node_singleton.node.eth.estimateGas(trx)
    gas_price: int = await node_singleton.gas_price
    return decimals.create_decimal(estimate_gas * gas_price) / decimals.create_decimal(10 ** 18)