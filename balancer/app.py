import asyncio
from src.init_sending_to_main_wallet import init_sending_to_main_wallet

async def main(loop):
    await asyncio.sleep(10)
    await init_sending_to_main_wallet(loop)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()