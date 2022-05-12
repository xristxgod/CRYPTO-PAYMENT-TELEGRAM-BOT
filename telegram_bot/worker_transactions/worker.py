import json
import asyncio
from asyncio import sleep as async_sleep

from tortoise.transactions import atomic
from aio_pika import connect_robust, IncomingMessage, RobustConnection, Channel

from worker_transactions.services.received import on_receiving
from worker_transactions.services.sended import on_sending_tx
from src.models import Wallet, TGUser
from config import Config, logger

@atomic()
async def __processing_message(message: IncomingMessage):
    async with message.process():
        msg: dict = json.loads(message.body)
        logger.error(f"Get msg: {msg}")
        tx = msg[1]['transactions'][0]
        for index, address in enumerate([tx['sender'], tx['recipient']]):
            wallet = await Wallet.get_or_none(address=address)
            if wallet is None:
                continue
            logger.error(f'WALLET: {wallet.address} | {wallet.user_id}')
            user = await TGUser.get(id=wallet.user_id)
            logger.error(f'WALLET FOUND')
            if index == 0:
                await on_sending_tx(user, tx)
            else:
                await on_receiving(user, tx)

async def receiving_transactions():
    while True:
        try:
            loop = asyncio.get_event_loop()
            connection = None
            while connection is None or connection.is_closed:
                try:
                    connection: RobustConnection = await connect_robust(Config.RABBITMQ_URL, loop=loop)
                except:
                    pass
                await async_sleep(10)
            logger.error(f'CONNECTED TO RABBITMQ')
            async with connection:
                channel: Channel = await connection.channel()
                __queue = await channel.declare_queue('messages', durable=True)
                async with __queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        await __processing_message(message=message)
        except Exception as error:
            logger.error(f"ERROR TRX PROCESSING: {error}")