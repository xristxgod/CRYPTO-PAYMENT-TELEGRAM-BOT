from decimal import Decimal

from tortoise.expressions import F

from worker.services.withdraw.decode_raw_tx import DecodedTx, decode_raw_tx
from src.models import Transaction, TransactionStatus, TGUser
from src.node import node_singleton
from src import models
from config import Config, decimals, logger

async def __create_transaction(from_address: str, to_address: str, amount: Decimal):
    try:
        from_address = node_singleton.node.toChecksumAddress(from_address)
        to_address = node_singleton.node.toChecksumAddress(to_address)
        nonce = await node_singleton.async_node.eth.get_transaction_count(from_address)

        _create_transaction = {
            "nonce": nonce,
            "from": from_address,
            "to": to_address,
            "value": node_singleton.async_node.toWei(amount, "ether"),
            "gasPrice": await node_singleton.gas_price,
            "gas": 21000
        }

        sender = from_address
        _create_transaction.update({'fromAddress': sender})
        return _create_transaction
    except Exception as e:
        logger.error(f'CREATE TX ERROR: {e}')
        return None

async def __sign_send_transaction(payload: dict, private_key: str) -> bool:
    try:
        transfer = {
            "nonce": payload['nonce'],
            "to": payload['to'],
            "value": payload['value'],
            "gasPrice": payload['gasPrice'],
            "gas": payload['gas'],
            "data": b"",
        }
        signed_transaction = node_singleton.node.eth.account.sign_transaction(
            transfer, private_key=private_key
        )
        sended = await node_singleton.async_node.eth.send_raw_transaction(
            transaction=node_singleton.async_node.toHex(signed_transaction.rawTransaction)
        )
        logger.error(f'SENDED: {sended}')
        tx: DecodedTx = decode_raw_tx(signed_transaction.rawTransaction.hex())
        return tx.hash_tx
    except Exception as e:
        logger.error(f'SEND ERROR: {e}')
        return None

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

async def __send_transaction(from_address, to_address, private_key, amount):
    try:
        tx_hex = await __create_transaction(from_address=from_address, to_address=to_address, amount=amount)
        return await __sign_send_transaction(payload=tx_hex, private_key=private_key)
    except Exception as e:
        logger.error(f'WITHDRAW ERROR: {e}')
        return None

async def send_money(user_id: int, tx_id: str, to_address: str, amount: Decimal):
    user = await TGUser.get(id=user_id)
    try:
        amount = decimals.create_decimal(amount)
        fee = decimals.create_decimal(await get_optimal_gas(Config.BSC_WITHDRAW_ADMIN_ADDRESS, to_address, amount))
        tx_hash = await __send_transaction(Config.BSC_WITHDRAW_ADMIN_ADDRESS, to_address, Config.BSC_WITHDRAW_ADMIN_PRIVATE_KEY, amount)
        if tx_hash is None:
            tx_status = False
            logger.error(f'WITHDRAW ERROR. HASI IS NONE: {tx_hash} | {user_id} | {tx_id} | {to_address} | {amount}')
        else:
            await Transaction.filter(id=tx_id).update(
                status=TransactionStatus.pending, fee=fee, tx_hash=tx_hash
            )
            tx_status = True
    except Exception as e:
        logger.error(f'WITHDRAW ERROR MAIN: {e} | {user_id} | {tx_id} | {to_address} | {amount}')
        tx_status = False
    if not tx_status:
        await Transaction.filter(id=tx_id).update(status=TransactionStatus.error)
        await models.TGUser.filter(id=user.id).update(balance=F('balance') + amount)
    return tx_status