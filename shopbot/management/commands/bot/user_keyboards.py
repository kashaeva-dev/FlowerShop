from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def give_buttons_with_occasion():
    inline_keyboard = [
        [
            InlineKeyboardButton(text='День Рождения', callback_data='цена'),
        ],
        [
            InlineKeyboardButton(text='Cвадьба', callback_data='цена'),
        ],
        [
            InlineKeyboardButton(text='В школу', callback_data='цена'),
        ],
        [
            InlineKeyboardButton(text='Без повода', callback_data='цена'),
        ],
        [
            InlineKeyboardButton(text='Другой повод', callback_data='какой повод'),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def give_buttons_with_prices():
    inline_keyboard = [
        [
            InlineKeyboardButton(text='До 500 рублей', callback_data='букет'),
        ],
        [
            InlineKeyboardButton(text='До 1000 рублей', callback_data='букет'),
        ],
        [
            InlineKeyboardButton(text='До 2000 рублей', callback_data='букет'),
        ],
        [
            InlineKeyboardButton(text='Не важно', callback_data='букет'),
        ],
    ]


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
