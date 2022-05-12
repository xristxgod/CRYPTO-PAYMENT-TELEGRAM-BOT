import os
from datetime import datetime
import xlsxwriter

from io import BytesIO
from requests import post

from src.models import TGUser, Wallet, Purchase, InviteTree, Table
from config import Config, logger

async def send_table_xlsx_service(user_id: int, table_id: int):
    filename = f'{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.xlsx'
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()

    row = 1
    col = 0

    worksheet.set_column(0, 1, 15)
    worksheet.set_column(2, 4, 30)
    worksheet.set_column(5, 5, 60)
    worksheet.write(0, col, 'ID')
    worksheet.write(0, col + 1, 'Table')
    worksheet.write(0, col + 2, 'Join time')
    worksheet.write(0, col + 3, 'First Name')
    worksheet.write(0, col + 4, 'Last Name')
    worksheet.write(0, col + 5, 'Username')
    worksheet.write(0, col + 6, 'Wallet')

    table = await Table.get(id=table_id)
    users_ids = await InviteTree.filter(ancestor_id=user_id, depth=1).values_list('child_id', flat=True)
    for p in await Purchase.filter(
            user_id__in=users_ids, table_id=table_id
    ).prefetch_related('user').order_by('user__created_at'):
        wallet = (await Wallet.get(user_id=p.user_id)).address
        worksheet.write(row, col, str(p.user.id))
        worksheet.write(row, col + 1, table.name)
        worksheet.write(row, col + 2, p.user.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        worksheet.write(row, col + 3, " " if p.user.first_name is None else p.user.first_name)
        worksheet.write(row, col + 4, " " if p.user.last_name is None else p.user.last_name)
        worksheet.write(row, col + 5, " " if p.user.username is None else p.user.username)
        worksheet.write(row, col + 6, wallet)
        row += 1

    workbook.close()

    with open(filename, 'rb') as file:
        file_io = BytesIO(file.read())
        file_io.seek(0)
    os.remove(filename)
    table = await Table.get(id=table_id)
    try:
        user = await TGUser.get(id=user_id)
        response = post(
            f'https://api.telegram.org/bot{Config.TOKEN}/sendDocument?chat_id={user.tg_id}',
            files={'document': (f'{table.name}.xlsx', file_io)}
        )
        if not response.ok:
            logger.error(f'SEND DOCS ERROR: {response.text}')
    except Exception as e:
        logger.error(f'SEND DOCS ERROR: {e}')
    return file_io, filename