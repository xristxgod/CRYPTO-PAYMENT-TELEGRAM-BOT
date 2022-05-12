from aiogram.utils.callback_data import CallbackData


close_cb = CallbackData('close', 'action')
admin_cb = CallbackData('admin_cb', 'action')


class BaseAction:
    close = 'close'
    choose = 'choose'


class Action:
    count = 'count'
    broadcast = 'broadcast'
    excel_users = 'excel_users'
    excel_transactions = 'excel_transactions'
    excel_programmes = 'excel_programmes'