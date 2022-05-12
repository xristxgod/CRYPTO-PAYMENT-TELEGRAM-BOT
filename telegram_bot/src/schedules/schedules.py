import asyncio
import aioschedule
from src.utils.lang_selector import lang_selector


async def scheduler():
    task = aioschedule.every(5).minutes.do(lang_selector.update)
    await task.run()

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)