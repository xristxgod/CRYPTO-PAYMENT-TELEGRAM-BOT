from celery import Celery
from tortoise import Tortoise

from config import Config

celery_app = Celery("worker", backend=Config.REDIS_URL, broker=Config.RABBITMQ_URL)
celery_app.conf.task_routes = {
     "worker.celery_worker.send_tg_message": "test-queue",
    "worker.celery_worker.withdraw": "test-queue",
    "worker.celery_worker.buy_new_programme": "test-queue",
    "worker.celery_worker.add_to_queue": "test-queue",
}

celery_app.conf.update(task_track_started=True)

async def init():
    await Tortoise.init(db_url=Config.DATABASE_URL, modules={"models": ["src.models"]})
    await Tortoise.generate_schemas()