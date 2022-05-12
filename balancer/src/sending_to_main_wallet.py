import json
import asyncio

from aio_pika import connect_robust, IncomingMessage, RobustConnection

from src.observer import observer
from src.__init__ import ExSend
from worker.celery_app import celery_app
from config import Config

async def __processing_message(message: IncomingMessage):
    async with message.process():
        msg: dict = json.loads(message.body)
        address = msg['address']
        can_go, wait_time = await observer.can_go(address)
        extra = {'countdown': wait_time} if not can_go and wait_time > 5 else {}
        celery_app.send_task(f'worker.celery_worker.send_transaction', args=[address], **extra)

async def sending_to_main_wallet(loop):
    while True:
        try:
            connection = None
            while connection is None or connection.is_closed:
                try:
                    connection: RobustConnection = await connect_robust(Config.RABBITMQ_URL, loop=loop)
                finally:
                    await ExSend.send_msg_to_kibana(msg=f'WAIT CONNECT TO RABBITMQ - SendToMainWalletQueue')
                await asyncio.sleep(2)

            async with connection:
                channel = await connection.channel()
                queue = await channel.declare_queue("SendToMainWalletQueue", durable=True)

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        await __processing_message(message)
        except Exception as error:
            await ExSend.send_exception_to_kibana(error, "ERROR INIT_SENDING_TO_MAIN_WALLET")