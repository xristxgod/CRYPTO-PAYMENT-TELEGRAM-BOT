from celery import Celery
from tortoise import Tortoise

from config import Config

celery_xlsx_app = Celery("worker", backend=Config.REDIS_URL, broker=Config.RABBITMQ_URL)
celery_xlsx_app.conf.task_routes = {
    "worker_xlsx.celery_worker.send_table_xlsx": "xlsx-queue",
    "worker_xlsx.celery_worker.send_partners_xlsx": "xlsx-queue",
}

celery_xlsx_app.conf.update(task_track_started=True)

async def init():
    await Tortoise.init(db_url=Config.DATABASE_URL, modules={'models': ['src.models']})
    await Tortoise.generate_schemas()
