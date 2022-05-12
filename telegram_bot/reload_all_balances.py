import asyncio

import aiohttp
from tortoise import Tortoise

from src.models import *
from src.node import node_singleton
from config import Config, decimals, logger

INT_WITHDRAW_ADMIN_ADDRESS = int(Config.BSC_WITHDRAW_ADMIN_ADDRESS, 0)
INT_ADMIN_ADDRESS = int(Config.BSC_ADMIN_ADDRESS, 0)

async def __rpc_request(method: str, *params):
    async with aiohttp.ClientSession(headers={'Content-Type': 'application/json'}) as session:
        async with session.post(
            Config.BSC_NODE_URL,
            json={
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "id": 1
            },
        ) as resp:
            data = await resp.json()
    return data['result']

async def _processing_transaction(tx, addresses, timestamp, all_transactions_hash_in_db):
    try:
        tx_hash = tx['hash'].hex()
        tx_addresses = []
        tx_from = None
        tx_to = None
        if tx['from'] is not None:
            tx_from = tx['from'].lower()
            tx_addresses.append(node_singleton.node.toChecksumAddress(tx_from))
        if tx['to'] is not None:
            tx_to = tx['to'].lower()
            tx_addresses.append(node_singleton.node.toChecksumAddress(tx_to))

        address = None
        for tx_address in tx_addresses:
            try:
                if int(tx_address, 0) in addresses:
                    address = tx_address.lower()
                    break
            except:
                continue

        if address is not None or tx_hash in all_transactions_hash_in_db:
            receipt = await __rpc_request('eth_getTransactionReceipt', tx_hash)

            if receipt is None or receipt['status'] == '0x0':
                return None

            if address is None:
                address = tx_from

            amount = str(node_singleton.node.fromWei(tx["value"], "ether"))
            fee = "%.18f" % (node_singleton.node.fromWei(int(receipt["gasUsed"], 0) * tx["gasPrice"], "ether"))
            values = {
                "time": timestamp,
                "transactionHash": tx_hash,
                "amount": amount,
                "fee": fee,
                "sender": tx_from,
                "recipient": tx_to,
            }
            return {"address": address, "transactions": [values]}
        return None
    except:
        return None

async def reload_balances():
    try:
        await Tortoise.init(
            db_url=Config.DATABASE_URL,
            modules={'models': ['src.models']}
        )
        await Tortoise.generate_schemas()
        print('START')
        addresses = [w.address for w in await Wallet.all()]
        with open('__blocks.txt', 'r') as f:
            blocks = list(set([int(x) for x in f.read().split('\n')]))
        blocks.sort()
        _length = len(blocks)
        for user in await TGUser.all().order_by('id'):
            balance = decimals.create_decimal('0.0')
            frozen_balance = decimals.create_decimal('0.0')
            for tx in await Transaction.filter(user_id=user.id, status=TransactionStatus.success).order_by('created_at'):
                if tx.type in [
                    TransactionType.to_user_from_queue,
                    TransactionType.referral,
                    TransactionType.tx_in,
                    TransactionType.from_frozen,
                    TransactionType.revoke,
                ]:
                    balance += tx.value
                elif tx.type == TransactionType.to_frozen:
                    frozen_balance += tx.value
                elif tx.type == TransactionType.tx_out:
                    balance -= tx.value
                elif tx.type in [
                    TransactionType.buy_table,
                    TransactionType.buy_queue
                ]:
                    if frozen_balance >= tx.value:
                        frozen_balance -= tx.value
                    else:
                        value = tx.value - frozen_balance
                        frozen_balance = 0
                        balance -= value
            logger.error(f'USER: {user.id} | BALANCE: {balance} | FROZEN: {frozen_balance}')
            await TGUser.filter(id=user.id).update(balance=balance, frozen_balance=frozen_balance)
    except Exception as e:
        logger.error(f'ERROR: {e}')

if __name__ == '__main__':
    asyncio.run(reload_balances())