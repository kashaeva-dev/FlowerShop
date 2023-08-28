from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import types

kb_choise_main_menu = [
    [types.KeyboardButton(text="Посмотреть каталог")],
    [types.KeyboardButton(text="Заказать консультацию")],
    [types.KeyboardButton(text="Заказы (для курьера)")],
    [types.KeyboardButton(text="Оформить заказ")],
    [types.KeyboardButton(text="О нас...")]
]
main_menu = types.ReplyKeyboardMarkup(
    keyboard=kb_choise_main_menu,
    resize_keyboard=True,)


kb_choise_order = [
    [types.KeyboardButton(text="Посмотреть заказы")],
    [types.KeyboardButton(text="Cтатусы заказов (изменение)")],
]
order_main_menu = types.ReplyKeyboardMarkup(
    keyboard=kb_choise_order,
    resize_keyboard=True,)

kb_choise_view = [
    [types.KeyboardButton(text="Посмотреть все 📊")],
    [types.KeyboardButton(text="Только новые 🆕")],
    [types.KeyboardButton(text="Меню заказов")]
]
order_choise = types.ReplyKeyboardMarkup(
    keyboard=kb_choise_view,
    resize_keyboard=True,)

kb_change_view = [
    [types.KeyboardButton(text="Принять 'Новый' в работу")],
    [types.KeyboardButton(text="Заказы - В работе")],
    [types.KeyboardButton(text="Указать - Доставлен")],
    [types.KeyboardButton(text="Указать - Отменен")],
    [types.KeyboardButton(text="Меню заказов")]
]

order_change_type = types.ReplyKeyboardMarkup(
    keyboard=kb_change_view,
    resize_keyboard=True,)