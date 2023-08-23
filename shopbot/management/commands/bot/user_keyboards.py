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

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
