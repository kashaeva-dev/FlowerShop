from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import KeyboardBuilder
from asgiref.sync import sync_to_async

from shopbot.models import Bouquet, Occasion


async def get_occasions_keyboard():
    occasions = await sync_to_async(Occasion.objects.all)()
    builder = KeyboardBuilder(button_type=InlineKeyboardButton)
    occasion_buttons = []
    async for occasion in occasions:
        occasion_button = InlineKeyboardButton(text=occasion.name, callback_data=f'occasion_{occasion.pk}')
        occasion_buttons.append(occasion_button)
    builder.row(*occasion_buttons, width=3)
    return InlineKeyboardMarkup(inline_keyboard=builder.export())


async def get_price_ranges_keyboard():
    inline_keyboard = [
        [
            InlineKeyboardButton(text='до 1000 рублей', callback_data='price_1000'),
        ],
        [
            InlineKeyboardButton(text='до 2000 рублей', callback_data='price_2000'),
        ],
        [
            InlineKeyboardButton(text='до 5000 рублей', callback_data='price_5000'),
        ],
        [
            InlineKeyboardButton(text='не важно', callback_data='price_1000000'),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

async def get_catalog_keyboard(bouquet_id: int):
    bouquet_number = await sync_to_async(Bouquet.objects.count)()
    next_bouquet_id = (int(bouquet_id) + 1) % bouquet_number
    if next_bouquet_id == 0:
        next_bouquet_id = bouquet_number
    prev_bouquet_id = (int(bouquet_id) - 1) % bouquet_number
    if prev_bouquet_id == 0:
        prev_bouquet_id = 1
    inline_keyboard = [
        [
            InlineKeyboardButton(text='<<', callback_data=f'catalog_{prev_bouquet_id}'),
            InlineKeyboardButton(text=f'{bouquet_id} из {bouquet_number}', callback_data='no_action'),
            InlineKeyboardButton(text='>>', callback_data=f'catalog_{next_bouquet_id}'),
        ],
        [
            InlineKeyboardButton(text='Посмотреть состав', callback_data='show_composition_{}'.format(bouquet_id)),
        ],
        [
            InlineKeyboardButton(text='Заказать', callback_data='start_order'),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def get_order_keybord():
    inline_keyboard = [
        [
            InlineKeyboardButton(text='📞 Заказать консультацию', callback_data='consultation'),
            InlineKeyboardButton(text='💐 Посмотреть всю коллекцию', callback_data='all_bouquets'),
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
