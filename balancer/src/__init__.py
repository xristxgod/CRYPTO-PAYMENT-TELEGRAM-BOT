import os
import sys
import traceback

import asyncpg

from config import Config, logger

class DB:
    @staticmethod
    async def __select_method(sql, data=None, is_row: bool = False):
        try:
            async with asyncpg.connect(Config.DATABASE_URL) as connection:
                if is_row:
                    return await connection.fetchrow(sql, data)
                return await connection.fetch(sql, data)
        except Exception as error:
            logger.error(f"ERROR: {error}")
            raise error

    @staticmethod
    async def get_private_key(address: str):
        try:
            return (await DB.__select_method(
                "SELECT private_key FROM wallet WHERE address = $1",
                address,
                is_row=True
            ))[0]
        except Exception as error:
            await ExSend.send_exception_to_kibana(error, 'ERROR GET PRIVATE KEY')
        return None

    @staticmethod
    async def get_wallets():
        try:
            return [address[0] for address in await DB.__select_method('SELECT address FROM wallet AND user_id != 1;')]
        except Exception as error:
            await ExSend.send_exception_to_kibana(error, 'ERROR GET PRIVATE KEY')
        return None

class ExSend:
    @staticmethod
    async def _send_msg_to_kibana(
            *, msg: str, code=None, tb=None, file_name=None, line=None, is_msg=False
    ):
        logger.error(f'KIBANA: {msg}')
        # index = ELASTIC_MSG_INDEX if is_msg else ELASTIC_LOG_INDEX
        # url = f'{ELASTIC_LOG_SERVER}/{index}/_doc'
        # time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # async with aiohttp.ClientSession(
        #         headers={'Content-Type': 'application/json'},
        #         auth=aiohttp.BasicAuth(ELASTIC_LOGIN, ELASTIC_PASSWORD)
        # ) as session:
        #     async with session.post(url, json={
        #         'Time': time,
        #         'Status': code,
        #         'Message': msg,
        #         'File': file_name,
        #         'Line': line,
        #         'Trace': tb,
        #         '@timestamp': datetime.now().isoformat()
        #     }) as resp:
        #         in_kibana = resp.ok
        # if code is None:
        #     logger.error(msg)
        # else:
        #     logger.error(
        #         f'EXCEPTION {time} || '
        #         f'Status: {code} || '
        #         f'Trace: {tb} || '
        #         f'File: {file_name} || '
        #         f'Line: {line} || '
        #         f'Sent to kibana: {in_kibana}'
        #     )
        # return in_kibana
        return True

    @staticmethod
    async def send_msg_to_kibana(msg: str):
        return await ExSend._send_msg_to_kibana(msg=msg, is_msg=True)

    @staticmethod
    async def send_error_to_kibana(*, msg: str, code: int):
        return await ExSend._send_msg_to_kibana(msg=msg, code=code)

    @staticmethod
    async def send_exception_to_kibana(e: Exception, msg: str = None):
        code = e.args[0]
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        tb = traceback.format_exc()
        line = exc_tb.tb_lineno
        return await ExSend._send_msg_to_kibana(
            msg=str(e) if msg is None else f'{msg} || {str(e)}',
            code=code, file_name=file_name, tb=tb, line=line
        )