import asyncio

from celery.signals import worker_process_init

from worker_xlsx.celery_app import celery_xlsx_app, init
from worker_xlsx.services.send_partners_xlsx_service import send_partners_xlsx_service
from worker_xlsx.services.send_table_xlsx_service import send_table_xlsx_service

def run_sync(f):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(f)

@worker_process_init.connect
def long_init_function(*args, **kwargs):
    run_sync(init())

@celery_xlsx_app.task(acks_late=True)
def send_table_xlsx(user_id: int, table_id: int):
    run_sync(send_table_xlsx_service(user_id, table_id))

@celery_xlsx_app.task(acks_late=True)
def send_partners_xlsx(user_id: int, depth: int):
    run_sync(send_partners_xlsx_service(user_id, depth))