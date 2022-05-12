from aiogram.utils.callback_data import CallbackData

struct_cb = CallbackData('struct_cb', 'action')
partners_list_cb = CallbackData('partners_list_cb', 'id', 'depth', 'page', 'action')

class Action:
    show_partners = 'show_partners'
    show_partners_depth = 'show_partners_depth'
    users_broadcast = 'users_broadcast'
    users_broadcast_revoke = 'users_broadcast_revoke'
    users_broadcast_agree = 'users_broadcast_agree'
    back = 'back'

    choose = 'choose'
    nothing = 'nothing'
    edit_page = 'edit_page'
    download_stats = 'download_stats'