from json import dumps
from typing import List, Dict

import asyncpg
from aio_pika import connect_robust, Message

from config import Config, logger

class DB:
    @staticmethod
    async def __select_method(sql, data=None, is_row: bool = False):
        try:
            async with asyncpg.connect(Config.DATABASE_URL) as connection:
                if is_row:
                    return await connection.fetchrow(sql, data)
                return await connection.fetch(sql, data)
        except Exception as error:
            logger.error(f"ERROR: {error}")
            raise error

    @staticmethod
    async def get_addresses_raw() -> List:
        """Get all addresses into table"""
        return [address[0] for address in await DB.__select_method("SELECT address FROM wallet;")]

    @staticmethod
    async def get_all_transactions_hash() -> List:
        """Get all transactions not processed."""
        return [address[0] for address in await DB.__select_method(
            "SELECT tx_hash from 'transaction' WHERE status=1 OR status=0"
        )]

    @staticmethod
    async def get_transaction_by_hash(transaction_hash: str) -> Dict:
        return await DB.__select_method(
            f"SELECT * from transaction WHERE (status=1 OR status=0) AND tx_hash='{transaction_hash}';",
            is_row=True
        )

class RabbitMQ:
    """ Class for sending processed data """
    @staticmethod
    async def send_founded_message(values) -> None:
        values = dumps(values)
        message = "{}".format(values)
        connection = await connect_robust(Config.RABBITMQ_URL)
        async with connection:
            queue_name = "messages"
            channel = await connection.channel()
            await channel.declare_queue(queue_name, durable=True)
            await channel.default_exchange.publish(
                Message(body=message.encode()), routing_key=queue_name,
            )

    @staticmethod
    async def request_for_sending_to_main_wallet(token: str, address: str):
        await RabbitMQ.__send_to_internal_rabbit(
            dumps({"token": token, "address": address, 'limit': "%.18f" % Config.SEND_TO_MAIN_WALLET_LIMIT}),
            'SendToMainWalletQueue'
        )

    @staticmethod
    async def got_fee_for_sending_token_to_main_wallet(address: str):
        await RabbitMQ.__send_to_internal_rabbit(
            dumps({"address": address, 'limit': "%.18f" % Config.SEND_TO_MAIN_WALLET_LIMIT}),
            'ReceiveTokenAndSendToMainWalletQueue'
        )

    @staticmethod
    async def __send_to_internal_rabbit(value, queue):
        connection = await connect_robust(Config.RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            await channel.declare_queue(queue, durable=True)
            await channel.default_exchange.publish(
                Message(body=value.encode()), routing_key=queue,
            )