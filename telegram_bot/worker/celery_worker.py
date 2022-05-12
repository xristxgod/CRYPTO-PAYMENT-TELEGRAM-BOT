import asyncio
from decimal import Decimal
from celery.signals import worker_process_init

from worker.celery_app import celery_app, init
from worker.services.add_to_queue import add_to_queue_service
from worker.services.buy_new_programme import buy_new_programme_service
from worker.services.withdraw.send_money import send_money
from worker.services.send_to_tg import send_to_tg_service

def run_sync(f):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(f)

@worker_process_init.connect
def long_init_function(*args, **kwargs):
    run_sync(init())

@celery_app.task(acks_late=True)
def send_tg_message(tg_id: int, text: str, keyboard=None):
    run_sync(send_to_tg_service(tg_id, text, keyboard))

@celery_app.task(acks_late=True)
def withdraw(user_id: int, tx_id, to_address: str, amount: Decimal):
    run_sync(send_money(user_id, tx_id, to_address, amount))

@celery_app.task(acks_late=True)
def buy_new_programme(user_id: int, table_id: int, is_with_queue: bool, purchase_id: int):
    run_sync(buy_new_programme_service(user_id, table_id, is_with_queue, purchase_id))

@celery_app.task(acks_late=True)
def add_to_queue(user_id: int, table_id: int):
    run_sync(add_to_queue_service(user_id, table_id))
