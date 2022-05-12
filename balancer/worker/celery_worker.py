import asyncio
from worker.celery_app import celery_app
from worker.services.send_transaction import send_transaction_service

def run_sync(f):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(f)

@celery_app.task(acks_late=True)
def send_transaction(address: str):
    run_sync(send_transaction_service(address))