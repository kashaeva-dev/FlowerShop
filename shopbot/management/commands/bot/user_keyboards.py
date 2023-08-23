from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import sync_to_async

from shopbot.models import Bouquet


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
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
