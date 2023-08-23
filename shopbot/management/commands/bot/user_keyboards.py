from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def get_catalog_keyboard(bouquet_id: int):
    # TODO: нужно исправить алгоритм пагинации
    next_bouquet_id = (int(bouquet_id) + 1) % 7
    if next_bouquet_id == 0:
        next_bouquet_id = 1
    prev_bouquet_id = (int(bouquet_id) + 7 - 1) % 7
    if prev_bouquet_id == 0:
        prev_bouquet_id = 7
    inline_keyboard = [
        [
            InlineKeyboardButton(text='<<', callback_data=f'catalog_{prev_bouquet_id}'),
            InlineKeyboardButton(text='>>', callback_data=f'catalog_{next_bouquet_id}'),
        ],
        [
            InlineKeyboardButton(text='Посмотреть состав', callback_data='show_composition_{}'.format(bouquet_id)),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
