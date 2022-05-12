from typing import List
from googletrans import Translator
from src.models import Lang, Phrase


class JSON:
    def __init__(self, code, text):
        self.code = code
        self.text = text

    def get(self):
        return {'code': self.code, 'text': self.text}


async def init_phrases():
    if not await Lang.exists(id=1):
        await Lang.create(id=1, name='🇷🇺 RU')
    if not await Lang.exists(id=2):
        await Lang.create(id=2, name='🇬🇧 EN')
    phrases: List[JSON] = [
        JSON(code='edit_success', text='Данные успешно сохранены'),

        JSON(
            code='welcome',
            text='👋 Добро пожаловать в Smartex Bot - инновационную платформу генерации дохода в криптовалюте BNB!\n'
                 '🔸🔸🔸\n'
                 'В разделе «💳 Баланс» вам доступен ввод и вывод средств.\n'
                 'В разделе «🔸 Программы Smartex» вы можете активировать участие в наших программах или посмотреть статус уже активированных.\n'
                 'Раздел «👥 Структура» предназначен для просмотра вашей партнёрской сети\n'
                 'В разделе «➕ Дополнительно» вы можете найти промо-материалы, ссылку на официальный канал, контакты техподдержки или поменять язык.\n'
                 '🔸🔸🔸\n'
                 '💸 Желаем вам огромного дохода в Smartex Bot!'
        ),
        JSON(code='not_found_inviter_id', text='Для доступа вы должны получить приглашение'),
        JSON(code='choose_lang', text='Выберите язык 💬'),
        JSON(code='btn_main_wallet', text='💳 Баланс'),
        JSON(code='btn_main_programmes', text='🔸 Программы Smartex'),
        JSON(code='btn_main_struct', text='👥 Структура'),
        JSON(code='btn_main_extra', text='➕ Дополнительно'),

        JSON(
            code='main_extra_text', text='В этом разделе вы можете найти промо-материалы, ссылку '
                                         'на официальный канал, контакты техподдержки или поменять язык.'
        ),
        JSON(code='main_extra_promo', text='📒 Промо-материалы'),
        JSON(code='main_extra_channel', text='📢 Официальный канал Smartex'),
        JSON(code='main_extra_support', text='👨‍🔧 Тех. поддержка'),
        JSON(code='main_extra_change_lang', text='🗣️ Сменить язык'),
        JSON(code='main_extra_admin', text='🔧 Администрирование'),

        JSON(code='extra_prezent_ru', text='📒 Презентация RU'),
        JSON(code='extra_prezent_en', text='📒 Презентация EN'),
        JSON(code='extra_video_ru', text='🎞️ Видео RU'),
        JSON(code='extra_video_en', text='🎞️ Видео EN'),
        JSON(code='extra_back', text='⬅ Назад'),

        JSON(code='wallet_unfreeze', text='❄️Разморозить'),
        JSON(code='wallet_add_money', text='📥 Пополнить'),
        JSON(code='wallet_withdraw', text='📤 Вывести'),
        JSON(code='wallet_my_buy', text='🛒 Покупки'),
        JSON(code='wallet_profit', text='💸 Доход'),
        JSON(code='wallet_data_list', text='📄 Список'),
        JSON(
            code='wallet_show_purchases_detail',
            text='Программа: {name}\n'
                 'Цена: {cost}\n'
                 'Дата приобретения: {time}'
        ),
        JSON(
            code='wallet_show_profit_detail',
            text='Сумма: {value}\n'
                 'Тип: {type}\n'
                 'Дата: {time}'
        ),

        JSON(
            code='main_wallet_text',
            text='💳 Основной счёт: {balance} BNB\n'
                 '💴 Накопительный счёт: {frozen_balance} BNB\n'
                 '\n'
                 'Средства с накопительного счёта могут быть использованы для оплаты программ Smartex\n'
                 '\n'
                 'Заработано всего\n'
                 '🔸 С программ Smartex: {program_profit} BNB\n'
                 '👥 Партнёрский бонус: {ref_bonus} BNB\n\n'
        ),
        JSON(
            code='main_wallet_add_money_text',
            text='<b>Для пополнения вашего баланса в Smartex bot отправьте BNB на указанный адрес:</b>\n'
                 '\n'
                 '<code>{address}</code>'
                 '\n'
                 '❗️Минимальная сумма пополнения 0.01 BNB\n'

        ),
        JSON(
            code='wallet_withdraw_enter_value',
            text='💬 <b>Введите сумму, которую хотите вывести</b>\n'
                 '❗️Минимальная сумма вывода 0.1 BNB, комиссия 0.01 BNB. Вывод средств производится в '
                 'автоматическом режиме в течении 2 часов.\n'
                 '\n'
                 'Максимальная сумма {balance} BNB\n'
        ),
        JSON(
            code='wallet_withdraw_value_less_then_0',
            text='Сумма вывода не может быть меньше чем 0.1 BNB'
        ),
        JSON(
            code='wallet_withdraw_value_enter_error_not_enough',
            text='На вашем счёте недостаточно средств'
        ),
        JSON(
            code='wallet_withdraw_enter_address',
            text='💬 Введите адрес BNB кошелька\n'
                 '\n'
                 'Внимание! Убедитесь что вы ввели верный адрес кошелька, в '
                 'противном случае есть риск потери средств'
        ),
        JSON(
            code='wallet_withdraw_sent',
            text='📤 <b>Заявка на вывод BNB успешно создана</b>'
        ),
        JSON(
            code='wallet_withdraw_revoke',
            text='Заявка на вывод отменена'
        ),
        JSON(
            code='wallet_withdraw_sent_error',
            text='При создании заявки произошла ошибка. Пожалуйста, попробуйте немного позже'
        ),
        JSON(
            code='wallet_withdraw_enter_miss',
            text='Вы ввели неверный формат данных. Пожалуйста, попробуйте снова'
        ),
        JSON(
            code='wallet_withdraw_accept_text',
            text='Подтвердите вывод средств\n'
                 '\n'
                 'Сумма {amount} BNB\n'
                 'Адрес кошелька <code>{address}</code>'
        ),
        JSON(code='wallet_withdraw_accept', text='Подтвердить'),
        JSON(code='wallet_withdraw_revoke', text='Отмена'),

        JSON(code='transaction_success', text='Операция с кошельком выполнена успешно\n'
                                              '\n'
                                              'Ваш баланс: {balance} BNB'),

        JSON(
            code='main_programmes_text',
            text='🔸 В Smartex Bot вам доступны 16 последовательно открывающихся программ, приносящие по 100% '
                 'прибыли при закрытии каждого цикла.'
        ),
        JSON(code='programmes_download_file', text='Пожалуйста, подождите пару секунд'),
        JSON(
            code='programmes_buy_text',
            text='{status} Smartex {name}\n'
                 '❗️Важно! Для активации программы после покупки необходимо выполнить одно из двух действий:\n'
                 '1️⃣ Пригласить на эту программу двух партнёров\n'
                 '2️⃣ Оплатить авто-активацию\n'
                 '\n'
                 'Баланс {balance} BNB\n'
                 '\n'
                 '{count} ваших партнеров учавствуют'
        ),
        JSON(
            code='programmes_detail_text',
            text='{status} <b>Smartex {name}</b>\n'
                 '\n'
                 'Дата приобритения {time}\n'
                 '\n'
                 '{count} ваших партнеров учавствуют\n'
                 '\n'
                 'Заработано средств {profit}'
        ),
        JSON(
            code='programmes_detail_text_without_queue',
            text='{status} <b>Smartex {name}</b>\n'
                 '❗️ Для активации программы вам необходимо выполнить одно из двух действий:\n'
                 '1️⃣ Пригласить на эту программу двух партнёров\n'
                 '2️⃣ Оплатить авто-активацию\n'
                 '\n'
                 'Дата приобритения {time}\n'
                 '\n'
                 '{count} ваших партнеров учавствуют\n'
                 '\n'
                 'Заработано средств {profit}'
        ),
        JSON(
            code='programmes_detail_text_is_inactive',
            text='{status} <b>Smartex {name}</b>\n'
                 'ℹ️ Программа будет доступна позже'
        ),
        JSON(code='programmes_btn_buy', text='💰 Участвовать ({cost} BNB)'),
        JSON(code='programmes_btn_buy_with_queue', text='💸 Участвовать с квалификацией ({cost} BNB)'),
        JSON(code='programmes_btn_buy_queue', text='💸 Получить квалификацию ({cost} BNB)'),
        JSON(code='programmes_btn_buy_back', text='⬅️Назад'),
        JSON(code='programmes_btn_queue', text='👥 Очередь {name}'),
        JSON(code='programmes_btn_download', text='🔽 Скачать статистику'),
        JSON(code='programmes_btn_buy_agree', text='✅ Подтвердите участие'),
        JSON(code='programmes_btn_buy_revoke', text='⬅️Назад'),
        JSON(
            code='programmes_buy_not_enough_balance',
            text='На вашем счёте недостаточно средств для покупки программы\n'
                 'Пополните ваш счёт'
        ),
        JSON(code='programmes_buy_error', text='Для покупки необходимо приобрести предыдущие программы!'),
        JSON(code='programmes_buy_success', text='Оплата прошла успешно!'),
        JSON(
            code='programmes_queue_info',
            text='{status} Smartex {name}\n'
                 '\n'
                 '🔁 Пройдено циклов: {count_user}\n'
                 '💸 Доход от программы: {profit} BNB'
        ),
        JSON(
            code='programmes_queue_info_not_exists',
            text='{status} Smartex {name}\n'
                 '\n'
                 'Последнее место получившее выплату {current_name}\n'
        ),
        JSON(
            code='referral_notify',
            text='💸 Получено реферальное вознаграждение\n'
                 '\n'
                 '💳 На основной счёт: {amount} BNB\n'
                 '🪙 На накопительный счёт: {frozen} BNB\n'
                 '\n'
                 'Основной счёт: {balance} BNB\n'
                 'Накопительный счёт: {frozen_balance} BNB'
        ),
        JSON(
            code='unfrozen_referral_notify',
            text='❄️Размороженно реферальное вознаграждение\n'
                 '\n'
                 '💳 На основной счёт: {amount} BNB\n'
                 '🪙 На накопительный счёт: {frozen} BNB\n'
                 '\n'
                 'Основной счёт: {balance} BNB\n'
                 'Накопительный счёт: {frozen_balance} BNB'
        ),
        JSON(
            code='queue_notify',
            text='🔥 Получено вознаграждение за пройденный цикл программы Smartex {name}\n'
                 '\n'
                 '💳 На основной счёт: {amount} BNB\n'
                 '🪙 На накопительный счёт: {frozen} BNB\n'
                 '\n'
                 'Основной счёт: {balance} BNB\n'
                 'Накопительный счёт: {frozen_balance} BNB'
        ),

        JSON(code='is_uplainer_message', text='💬 Сообщение от аплайнера:'),
        JSON(
            code='struct_show_partners_main_text',
            text='<b>Всего пользователей в Smartex Bot: {count_all}</b>\n'
                 '\n'
                 '👥 Ваша структура / заработано\n'
                 '{counts}'
                 '\n'
                 '<b>🔗 Ваша партнёрская ссылка:</b> {ref}\n'
                 '\n'
                 'Всего в структуре: {count}\n'
                 'Заработано всего: {profit} BNB'
        ),
        JSON(code='struct_count_lines_row', text='{depth} ур. {count} / {referrals} BNB\n'),
        JSON(code='struct_show_partners', text='👥 Список партнеров'),
        JSON(code='struct_show_partners_depth', text='Выберите линию'),
        JSON(code='struct_show_partners_download_xlsx', text='📈 Выгрузить в EXCEL'),
        JSON(code='struct_show_partners_download_xlsx_start', text='⏰ Пожалуйста, подождите пару секунд'),
        JSON(
            code='struct_show_partners_detail',
            text='Партнер {name}\n'
                 '\n'
                 'Программы партнера:\n'
        ),
        JSON(code='struct_show_send_to_partners', text='🗣️ Написать первой линии'),
        JSON(
            code='struct_show_send_to_partners_text',
            text='Введите текст который хотите отправить своим партнерам или нажмите /close'
        ),
        JSON(code='struct_show_send_to_partners_agree', text='🗣️ Отправить рассылку?'),
        JSON(code='struct_show_send_to_partners_btn_agree', text='❓ Отправить'),
        JSON(code='struct_show_send_to_partners_btn_revoke', text='⬅️Отмена'),
        JSON(code='struct_show_send_to_partners_started', text='✅ Рассылка запущена'),
        JSON(code='struct_show_send_to_partners_btn_back', text='⬅️Назад'),

        JSON(code='revoke_queue_tx', text='Ваша заявка на повторное добавление в очередь была отклонена')
    ]
    translator = Translator()
    for phrase in phrases:
        for lang in await Lang.all():
            if not await Phrase.exists(code=phrase.code, lang_id=lang.id):
                if lang.id == 1:
                    await Phrase.create(**phrase.get(), lang_id=lang.id)
                else:
                    res = translator.translate(phrase.text, src='ru')
                    await Phrase.create(
                        code=phrase.code, lang_id=lang.id,
                        text=res.text
                    )