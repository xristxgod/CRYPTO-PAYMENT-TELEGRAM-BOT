from aiogram.utils.callback_data import CallbackData

wallet_cb = CallbackData('wallet_cb', 'action')
purchases_list_cb = CallbackData('purchases_list_cb', 'id', 'page', 'action')
profit_list_cb = CallbackData('profit_list_cb', 'id', 'page', 'action')

class Action:
    unfreeze = 'unfreeze'
    add_money = 'add_money'
    withdraw = 'withdraw'
    my_buy = 'my_buy'
    my_profit = 'my_profit'

    withdraw_agree = 'withdraw_agree'
    withdraw_revoke = 'withdraw_revoke'

    choose = 'choose'
    nothing = 'nothing'
    edit_page = 'edit_page'
    download_stats = 'download_stats'
    back = 'back'
