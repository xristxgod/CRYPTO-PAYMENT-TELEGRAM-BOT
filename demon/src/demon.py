import os
import json
import asyncio
from asyncio import create_task
from uuid import uuid4
from time import sleep
from time import time as t
from datetime import datetime, timedelta
from typing import Optional

import aiohttp
import aiofiles
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

from src.__init__ import DB, RabbitMQ, ExSend
from src.utils import Utils
from src.types import INT_ADMIN_ADDRESS, INT_WITHDRAW_ADMIN_ADDRESS, ERC20_ABI
from config import Config, logger
from config import ERROR, NOT_SEND, LAST_BLOCK

class TransactionsDemon:
    rabbit: RabbitMQ = RabbitMQ()
    abi = ERC20_ABI
    NODE_URL = Config.BSC_NODE_URL

    def __init__(self):
        self._node: Optional[Web3] = None
        self.connect()
        sleep(3)

    def connect(self):
        provider: HTTPProvider = HTTPProvider(self.NODE_URL)
        self._node = Web3(provider)
        if self.NODE_URL.startswith('https'):
            self._node.middleware_onion.inject(geth_poa_middleware, layer=0)

    async def __rpc_request(self, method: str, *params):
        async with aiohttp.ClientSession(headers={'Content-Type': 'application/json'}) as session:
            async with session.post(
                self.NODE_URL,
                json={
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": params,
                    "id": 1
                },
            ) as resp:
                data = await resp.json()
        return data['result']

    async def __get_block_by_number(self, number: int):
        return self._node.eth.get_block(number)

    async def _processing_transaction(self, tx, addresses, timestamp, all_transactions_hash_in_db):
        try:
            tx_hash = tx['hash'].hex()
            tx_addresses = []
            tx_from = None
            tx_to = None
            if tx['from'] is not None:
                tx_from = tx['from'].lower()
                tx_addresses.append(self._node.toChecksumAddress(tx_from))
            if tx['to'] is not None:
                tx_to = tx['to'].lower()
                tx_addresses.append(self._node.toChecksumAddress(tx_to))

            address = None
            for tx_address in tx_addresses:
                try:
                    if int(tx_address, 0) in addresses:
                        address = tx_address.lower()
                        break
                except:
                    continue

            if address is not None or tx_hash in all_transactions_hash_in_db:
                receipt = await self.__rpc_request('eth_getTransactionReceipt', tx_hash)

                if receipt is None or receipt['status'] == '0x0':
                    return None

                if address is None:
                    address = tx_from

                amount = str(self._node.fromWei(tx["value"], "ether"))
                fee = "%.18f" % (self._node.fromWei(int(receipt["gasUsed"], 0) * tx["gasPrice"], "ether"))
                values = {
                    "time": timestamp,
                    "datetime": str(Utils.convert_time(str(timestamp)[:10])),
                    "transactionHash": tx_hash,
                    "amount": amount,
                    "fee": fee,
                    "sender": tx_from,
                    "recipient": tx_to,
                }
                return {"address": address, "transactions": [values]}
            return None
        except Exception as error:
            await ExSend.send_exception_to_kibana(error, f'PROC TX ERROR: {error} | {tx["from"]} | {tx["to"]}')
            return None

    async def __processing_block(self, block_number: int, addresses):
        try:
            logger.error(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | PROCESSING BLOCK: {block_number}')
            block = self._node.eth.get_block(block_number, True)

            if 'transactions' in block.keys() and isinstance(block['transactions'], list):
                count_trx = len(block['transactions'])
            else:
                return True
            if count_trx == 0:
                return True
            all_transactions_hash_in_db = await DB.get_all_transactions_hash()
            trx = await asyncio.gather(*[
                self._processing_transaction(
                    tx=block['transactions'][index],
                    addresses=addresses,
                    timestamp=block['timestamp'],
                    all_transactions_hash_in_db=all_transactions_hash_in_db
                )
                for index in range(count_trx)
            ])
            trx = list(filter(lambda x: x is not None, trx))
            if len(trx) > 0:
                await asyncio.gather(*[
                    self._send_to_rabbit_mq(
                        package=tx,
                        addresses=addresses,
                        all_transactions_hash_in_db=all_transactions_hash_in_db,
                        block_number=block_number
                    ) for tx in trx
                ])
            return True
        except Exception as error:
            await ExSend.send_exception_to_kibana(error, 'BLOCK ERROR')
            return False

    async def _send_to_rabbit_mq(self, package, addresses, all_transactions_hash_in_db, block_number) -> None:
        """Send collected data to queue"""
        package_for_sending = [{"network": f"bsc_bip20_bnb", "block": block_number}, package]
        try:
            recipient = package['transactions'][0]['recipient']
            recipient_int = int(recipient, 0)

            sender = package['transactions'][0]['sender']
            sender_int = int(sender, 0)

            if (sender_int == INT_WITHDRAW_ADMIN_ADDRESS) and (recipient_int not in addresses):
                tx_hash = package["transactions"][0]["transactionHash"]
                if tx_hash in all_transactions_hash_in_db:
                    package_for_sending[1]['transactions'] = [await Utils.get_transaction_in_db(
                        transaction_hash=tx_hash,
                        transaction=package['transactions'][0]
                    )]
                await self.rabbit.send_founded_message(package_for_sending)
                await ExSend.send_msg_to_kibana(msg=f'SENDING FROM MAIN WALLET: {package_for_sending}')
            elif recipient_int != INT_ADMIN_ADDRESS and recipient_int != INT_WITHDRAW_ADMIN_ADDRESS:
                # If it's not sending to main wallet (receiving)
                await self.rabbit.send_founded_message(package_for_sending)
                await self.rabbit.request_for_sending_to_main_wallet(token='bnb', address=recipient)
                await ExSend.send_msg_to_kibana(msg=f'RECEIVE NEW TX: {package_for_sending}')
        except Exception as error:
            await ExSend.send_exception_to_kibana(error, f'SENDING TO MQ ERROR: {package_for_sending}')
            async with aiofiles.open(ERROR, 'a', encoding='utf-8') as file:
                # If an error occurred on the RabbitMQ side, write about it.
                await file.write(f"Error: {package_for_sending} | RabbitMQ not responding {error} \n")
            new_not_send_file = os.path.join(NOT_SEND, f'{uuid4()}.json')
            async with aiofiles.open(new_not_send_file, 'w') as file:
                # Write all the verified data to a json file, and do not praise the work
                await file.write(json.dumps(package_for_sending))

    async def get_node_block_number(self):
        return int(self._node.eth.block_number)

    async def __get_last_block_number(self):
        async with aiofiles.open(LAST_BLOCK, "r") as file:
            current_block = await file.read()
        if current_block:
            return int(current_block)
        else:
            return await self.get_node_block_number()

    @staticmethod
    async def __save_block_number(block_number: int):
        async with aiofiles.open(LAST_BLOCK, "w") as file:
            await file.write(str(block_number))

    async def __run(self):
        """ The script runs all the time """
        start = await self.__get_last_block_number()
        pack_size = 1
        while True:
            end = await self.get_node_block_number()
            if end - start < pack_size:
                await asyncio.sleep(3)
            else:
                start_time = t()
                addresses = await DB.get_addresses()
                success = await asyncio.gather(*[
                    self.__processing_block(block_number=block_number, addresses=addresses)
                    for block_number in range(start, start + pack_size)
                ])
                logger.error("End block: {}. Time taken: {} sec".format(
                    start, str(timedelta(seconds=int(t() - start_time)))
                ))
                if all(success):
                    start += pack_size
                    await self.__save_block_number(start)
                else:
                    await ExSend.send_error_to_kibana(msg=f'BLOCK {start} ERROR. RUN BLOCK AGAIN', code=-1)
                    continue

    async def __start_in_range(self, start_block, end_block):
        for block_number in range(start_block, end_block):
            addresses = await DB.get_addresses()
            await self.__processing_block(block_number=block_number, addresses=addresses)

    async def __send_all_from_folder_not_send(self):
        files = os.listdir(NOT_SEND)
        addresses = await DB.get_addresses()
        all_transactions_hash_in_db = await DB.get_all_transactions_hash()

        for file_name in files:
            try:
                path = os.path.join(NOT_SEND, file_name)
                with open(path, 'r') as file:
                    values = json.loads(file.read())
                block = values[0]['block']
                await self._send_to_rabbit_mq(values, addresses, all_transactions_hash_in_db, block)
                os.remove(path)
            except:
                continue

    async def start(self, start_block: int = None, end_block: int = None, *args):
        if start_block and end_block:
            await self.__start_in_range(start_block, end_block)
        elif start_block and not end_block:
            await self.__start_in_range(start_block, await self.get_node_block_number() + 1)
        elif not start_block and end_block:
            await self.__start_in_range(await self.get_node_block_number(), end_block)
        else:
            await ExSend.send_msg_to_kibana(msg=f"DEMON IS STARTING")
            create_task(self.__send_all_from_folder_not_send())
            await self.__run()