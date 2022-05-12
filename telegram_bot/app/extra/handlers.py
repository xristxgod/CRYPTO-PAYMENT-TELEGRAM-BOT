from app.extra.keyboards import extra_menu_keyboard, extra_cb, Action, promo_keyboard
from app.extra.states import *
from app.base.keyboards import admin_keyboard, main_keyboard
from app.start.keyboards import choose_lang_cb, lang_choose_keyboard
from app.bot_init import *
from src.models import TGUser, Purchase, Transaction, TransactionType, TransactionStatus
from config import Config

@dp.message_handler(lambda message: message.text in lang_selector.get_hotkey('btn_main_extra'))
async def open_extras(message: types.Message, state: FSMContext, db_user: UserData):
    if state is not None:
        await state.finish()
    await send_message(message.chat.id, 'main_extra_text', 1, await extra_menu_keyboard(db_user))

@dp.callback_query_handler(extra_cb.filter(action=Action.edit_lang))
async def start_edit_lang(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await EditDataForm.lang_id.set()
    await send_message(db_user.id, 'choose_lang', db_user.lang_id, await lang_choose_keyboard())
    await query.message.delete()

@dp.callback_query_handler(choose_lang_cb.filter(), state=EditDataForm.lang_id)
async def get_user_lang(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    lang_id = int(callback_data['id'])
    await TGUser.filter(id=db_user.db_id).update(lang_id=lang_id,)
    db_user = UserData(data=await TGUser.get(id=db_user.db_id))
    await send_msg_text(db_user.id, 'OK', await main_keyboard(db_user))
    await send_message(db_user.id, 'edit_success', db_user.lang_id, await extra_menu_keyboard(db_user))
    await state.finish()
    await query.message.delete()

@dp.callback_query_handler(extra_cb.filter(action=Action.promo))
async def open_promo(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await send_message(db_user.id, 'main_extra_promo', db_user.lang_id, await promo_keyboard(db_user))

@dp.callback_query_handler(extra_cb.filter(action=Action.open_admin))
async def open_admin(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    if db_user.id not in Config.ADMIN_IDS:
        return
    tx_in = sum(await Transaction.filter(type=TransactionType.tx_in).values_list("value", flat=True))
    tx_out = sum(await Transaction.filter(type=TransactionType.tx_out, status=TransactionStatus.success).values_list("value", flat=True))
    tx_out_wait = sum(await Transaction.filter(type=TransactionType.tx_out, status=TransactionStatus.created).values_list("value", flat=True))
    text = (
        f'Total users: {await TGUser.all().count()}\n'
        f'Total paid: {await Purchase.filter(table_id=1).count()}\n'
        f'Total deposits in the amount of: {"%.6f" % tx_in} BNB\n'
        f'Total amount of confirmed conclusions: {"%.6f" % tx_out} BNB\n'
        f'Total pending conclusions: {"%.6f" % tx_out_wait} BNB'
    )
    await send_msg_text(db_user.id, text, await admin_keyboard())
    await query.message.delete()