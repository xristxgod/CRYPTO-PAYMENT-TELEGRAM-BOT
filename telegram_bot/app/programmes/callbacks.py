from aiogram.utils.callback_data import CallbackData

programmes_cb = CallbackData('programmes_cb', 'id', 'action')

class Action:
    choose = 'choose'
    buy = 'buy'
    buy_qualification_only = 'buy_qualification_only'
    buy_with_qualification = 'buy_with_qualification'
    buy_agree = 'buy_agree'
    buy_with_qualification_agree = 'buy_with_qualification_agree'
    buy_qualification_only_agree = 'buy_qualification_only_agree'
    download_stats = 'download_stats'
    show_queue = 'show_queue'
    back = 'back'
    revoke = 'revoke'
