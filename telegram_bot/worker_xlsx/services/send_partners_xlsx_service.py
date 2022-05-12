import os
from datetime import datetime
import xlsxwriter

from io import BytesIO
from requests import post

from src.models import TGUser, InviteTree
from app import bot
from config import Config, logger

async def send_partners_xlsx_service(user_id: int, depth: int):
    filename = f'{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.xlsx'
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()

    row = 1
    col = 0

    worksheet.set_column(0, 1, 15)
    worksheet.set_column(2, 4, 30)
    worksheet.set_column(5, 5, 60)
    worksheet.write(0, col, 'ID')
    worksheet.write(0, col + 1, 'Join time')
    worksheet.write(0, col + 2, 'First Name')
    worksheet.write(0, col + 3, 'Last Name')
    worksheet.write(0, col + 4, 'Username')
    worksheet.write(0, col + 5, 'URL')

    url = f'https://t.me/{(await bot.get_me()).username}?start'

    users_ids = await InviteTree.filter(ancestor_id=user_id, depth=depth).values_list('child_id', flat=True)
    for user in await TGUser.filter(id__in=users_ids).order_by('created_at'):
        worksheet.write(row, col, str(user.id))
        worksheet.write(row, col + 1, user.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        worksheet.write(row, col + 2, " " if user.first_name is None else user.first_name)
        worksheet.write(row, col + 3, " " if user.last_name is None else user.last_name)
        worksheet.write(row, col + 4, " " if user.username is None else user.username)
        worksheet.write(row, col + 5, f'{url}={user.id}')
        row += 1

    workbook.close()
    with open(filename, 'rb') as file:
        file_io = BytesIO(file.read())
        file_io.seek(0)
    os.remove(filename)

    try:
        user = await TGUser.get(id=user_id)
        response = post(
            f'https://api.telegram.org/bot{Config.TOKEN}/sendDocument?chat_id={user.tg_id}',
            files={'document': ('partners.xlsx', file_io)}
        )
        if not response.ok:
            logger.error(f'SEND DOCS ERROR: {response.text}')
    except Exception as e:
        logger.error(f'SEND DOCS ERROR: {e}')
    return file_io, filename