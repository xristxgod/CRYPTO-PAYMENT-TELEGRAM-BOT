import os
from datetime import datetime
import xlsxwriter
from io import BytesIO

from src.models import TGUser, Wallet, Transaction, Table, Purchase, Queue

async def get_users_xlsx() -> (BytesIO, str):
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
    worksheet.write(0, col + 5, 'Wallet')

    for user in await TGUser.all().prefetch_related('wallet'):
        wallet = (await Wallet.get(user_id=user.id)).address
        worksheet.write(row, col, str(user.id))
        worksheet.write(row, col + 1, user.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        worksheet.write(row, col + 2, " " if user.first_name is None else user.first_name)
        worksheet.write(row, col + 3, " " if user.last_name is None else user.last_name)
        worksheet.write(row, col + 4, " " if user.username is None else user.username)
        worksheet.write(row, col + 5, wallet)
        row += 1

    workbook.close()
    with open(filename, 'rb') as file:
        file_io = BytesIO(file.read())
        file_io.seek(0)
    os.remove(filename)
    return file_io, filename


async def get_status(st):
    if st == 0:
        status = 'Создано'
    elif st == 1:
        status = 'Ждёт подтверждения'
    elif st == 2:
        status = 'Успешно'
    else:
        status = 'Ошибка'
    return status


async def get_tx_type(t):
    if t == 1:
        status = 'Ждёт подтверждения'
    elif t == 2:
        status = 'Выплата из очереди'
    elif t == 3:
        status = 'Реферальное'
    elif t == 4:
        status = 'Пополнение'
    elif t == 5:
        status = 'Вывод'
    elif t == 6:
        status = 'Заморозка'
    elif t == 7:
        status = 'Разморозка'
    else:
        status = 'Покупка стола'
    return status


async def get_tx_xlsx() -> (BytesIO, str):
    filename = f'{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.xlsx'
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()

    row = 1
    col = 0

    worksheet.set_column(0, 1, 20)
    worksheet.set_column(2, 4, 30)
    worksheet.set_column(5, 6, 60)
    worksheet.set_column(7, 10, 30)
    worksheet.set_column(11, 12, 60)
    worksheet.set_column(13, 13, 30)
    worksheet.write(0, col, 'ID')
    worksheet.write(0, col + 1, 'Hash')
    worksheet.write(0, col + 2, 'First Name')
    worksheet.write(0, col + 3, 'Last Name')
    worksheet.write(0, col + 4, 'Username')
    worksheet.write(0, col + 5, 'Created At')
    worksheet.write(0, col + 6, 'Update At')
    worksheet.write(0, col + 7, 'Value')
    worksheet.write(0, col + 8, 'Fee')
    worksheet.write(0, col + 9, 'Status')
    worksheet.write(0, col + 10, 'Type')
    worksheet.write(0, col + 11, 'Sender')
    worksheet.write(0, col + 12, 'Recipient')
    worksheet.write(0, col + 13, 'Table')

    for tx in await Transaction.all().prefetch_related('user', 'table'):

        worksheet.write(row, col, str(tx.id))
        worksheet.write(row, col + 1, str(tx.tx_hash))
        worksheet.write(row, col + 2, " " if tx.user.first_name is None else tx.user.first_name)
        worksheet.write(row, col + 3, " " if tx.user.last_name is None else tx.user.last_name)
        worksheet.write(row, col + 4, " " if tx.user.username is None else tx.user.username)
        worksheet.write(row, col + 5, tx.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        worksheet.write(row, col + 6, tx.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
        worksheet.write(row, col + 7, "%.8f" % tx.value)
        worksheet.write(row, col + 8, "%.8f" % tx.fee)
        worksheet.write(row, col + 9, await get_status(tx.status))
        worksheet.write(row, col + 10, await get_tx_type(tx.type))
        worksheet.write(row, col + 11, tx.sender if tx.sender is not None else " ")
        worksheet.write(row, col + 12, tx.recipient if tx.recipient is not None else " ")
        worksheet.write(row, col + 13, tx.table.name if tx.table is not None else " ")
        row += 1

    workbook.close()
    with open(filename, 'rb') as file:
        file_io = BytesIO(file.read())
        file_io.seek(0)
    os.remove(filename)
    return file_io, filename


async def get_tables_xlsx() -> (BytesIO, str):
    filename = f'{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.xlsx'
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()

    row = 1
    col = 0

    worksheet.set_column(0, 1, 15)
    worksheet.set_column(2, 4, 30)
    worksheet.set_column(5, 5, 60)
    worksheet.write(0, col, 'ID')
    worksheet.write(0, col + 1, 'Name')
    worksheet.write(0, col + 2, 'Cost')
    worksheet.write(0, col + 3, 'Purchases')
    worksheet.write(0, col + 4, 'Unique users in Queue')
    worksheet.write(0, col + 5, 'All in Queue')

    for t in await Table.all():
        count_all = await Queue.filter(table_id=t.id).values_list('user_id', flat=True)

        worksheet.write(row, col, str(t.id))
        worksheet.write(row, col + 1, t.name)
        worksheet.write(row, col + 2, t.cost)
        worksheet.write(row, col + 3, await Purchase.filter(table_id=t.id).count())
        worksheet.write(row, col + 4, len(set(count_all)))
        worksheet.write(row, col + 5, len(count_all))
        row += 1

    workbook.close()
    with open(filename, 'rb') as file:
        file_io = BytesIO(file.read())
        file_io.seek(0)
    os.remove(filename)
    return file_io, filename