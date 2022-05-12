import json
import decimal
from typing import Optional, Dict
from datetime import datetime

from src.services.decode_raw_tx import DecodedTx, decode_raw_tx
from src.services.node import node_singleton
from config import decimals

async def create_transaction(from_address: str, to_address: str, amount: decimal.Decimal) -> Optional[dict]:
    try:
        from_address = node_singleton.node.toChecksumAddress(from_address)
        to_address = node_singleton.node.toChecksumAddress(to_address)
        nonce = await node_singleton.async_node.eth.get_transaction_count(from_address)
    except:
        return None
    try:
        _create_transaction = {
            "nonce": nonce,
            "from": from_address,
            "to": to_address,
            "value": node_singleton.async_node.toWei(amount, "ether"),
            "gasPrice": await node_singleton.gas_price,
            "gas": 21000
        }

        node_fee = decimals.create_decimal(_create_transaction['gas']) / (10 ** 8)
        sender = from_address
        _create_transaction.update({'fromAddress': sender})
        tx_hex = json.dumps(_create_transaction)
        return {
            'fee': "%.8f" % node_fee,
            'maxFeeRate': _create_transaction['gasPrice'],
            'createTxHex': tx_hex,
        }
    except:
        return None

async def sign_send_transaction(payload: str, private_key: str) -> Dict:
    payload = json.loads(payload)
    from_address = payload.pop('fromAddress', None)
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
    await node_singleton.async_node.eth.send_raw_transaction(
        transaction=node_singleton.async_node.toHex(signed_transaction.rawTransaction)
    )
    tx: DecodedTx = decode_raw_tx(signed_transaction.rawTransaction.hex())
    value = decimals.create_decimal(tx.value) / (10 ** 18)
    node_fee = decimals.create_decimal(tx.gas) / (10 ** 8)
    return {
        'time': int(round(datetime.now().timestamp())),
        'transactionHash': tx.hash_tx,
        'amount': "%.18f" % value,
        'fee': "%.8f" % node_fee,
        'sender': from_address,
        'recipient': tx.to
    }