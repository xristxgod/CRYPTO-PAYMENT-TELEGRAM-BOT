from aiohttp import ClientSession

from config import Config, logger


async def send_to_tg_service(tg_id: int, text: str, keyboard=None):
    s = False
    try:
        extra = {'reply_markup': keyboard} if keyboard is not None else {}
        async with ClientSession() as session:
            async with session.get(
                f'https://api.telegram.org/bot{Config.TOKEN}/sendMessage',
                params={
                    'chat_id': tg_id,
                    'text': text,
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': 1,
                    'protect_content': 1,
                    **extra
                }
            ) as response:
                s = response.ok
    except Exception as error:
        logger.error(f'SEND: {error}')
    return s