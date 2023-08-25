import logging
import os

from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.filters import Command
from aiogram import F
from asgiref.sync import sync_to_async
from environs import Env

from conf.settings import BASE_DIR
from shopbot.models import Client, Advertisement, Staff, Bouquet, Order
from shopbot.management.commands.bot.user_keyboards import get_catalog_keyboard
from shopbot.management.commands.bot.user_menu import *
from aiogram.utils.keyboard import ReplyKeyboardBuilder


logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d - %(levelname)-8s - %(asctime)s - %(funcName)s - %(name)s - %(message)s'
    )

logger = logging.getLogger(__name__)


env: Env = Env()
env.read_env()

bot: Bot = Bot(token=env('TG_BOT_API'), parse_mode='HTML')

router = Router()


@router.message(Command(commands=["start"]))
async def start_command_handler(message: Message):
    staff = await sync_to_async(Staff.objects.filter(telegram_id=message.from_user.id).first)()
    if staff:
        await message.answer('Привет!\nМы тебя уже знаем! Ты наш сотрудник!')
        return

    user_id = message.from_user.id
    refer_id = None

    if " " in message.text:
        refer_id = message.text.split(" ")[1]

    try:
        refer_id = int(refer_id)
    except TypeError:
        refer_id = None

    advertisement = None
    if refer_id:
        advertisement = await sync_to_async(Advertisement.objects.filter(refer_id=refer_id).first)()

    client, created = await sync_to_async(Client.objects.get_or_create)(telegram_id=user_id)

    if created:
        client.advertisement = advertisement
        client.first_name = message.from_user.first_name
        await sync_to_async(client.save)()
        await message.answer('Привет!\nМы тебя зарегистрировали!')
    else:
        await message.answer('Привет!\nМы тебя уже знаем!')


@router.message(Command(commands=['catalog']))
async def show_start_catalog_handler(message: Message):
    bouquet = await sync_to_async(Bouquet.objects.all().first)()
    image_path = os.path.join(BASE_DIR, bouquet.image.url.lstrip('/'))
    logger.info(f'picture path {image_path}')
    photo = FSInputFile(image_path)
    await bot.send_photo(
        chat_id=message.from_user.id,
        caption=f'{bouquet.name.upper()}\n\n'
        f'<b>💡 Смысл букета</b>:\n\n{bouquet.meaning}\n\n'
        f'<b>💰 {bouquet.price} руб.</b>',
        photo=photo,
        reply_markup=await get_catalog_keyboard(bouquet.id)
    )


@router.callback_query(F.data.startswith('catalog_'))
async def show_more_catalog_handler(callback: CallbackQuery):
    bouquet_id = callback.data.split('_')[-1]
    logger.info(f'bouquet_id {bouquet_id}')
    bouquet = await sync_to_async(Bouquet.objects.filter(pk=bouquet_id).first)()
    image_path = os.path.join(BASE_DIR, bouquet.image.url.lstrip('/'))
    logger.info(f'picture path {image_path}')
    photo = FSInputFile(image_path)
    await bot.edit_message_media(chat_id=callback.from_user.id,
                                 message_id=callback.message.message_id,
                                 media=InputMediaPhoto(media=photo,
                                                       caption=f'{bouquet.name.upper()}\n\n'
                                                               f'<b>💡 Смысл букета</b>:\n\n{bouquet.meaning}\n\n'
                                                               f'<b>💰 {bouquet.price} руб.</b>'),
                                 reply_markup=await get_catalog_keyboard(bouquet.id))


# @router.callback_query(F.data.startswith('show_composition_'))
# async def show_composition_handler(callback: CallbackQuery):
#     bouquet_id = callback.data.split('_')[-1]
#     bouquet = await sync_to_async(Bouquet.objects.filter(pk=bouquet_id)
#                                   .prefetch_related('flowers')
#                                   .prefetch_related('greenery')
#                                   .first)()
#     flowers = []
#     async for flower1 in bouquet.flowers.all():
#         flowers.append(f'{flower1.name}')
#     flowers = ''.join(flowers)
#     greeneries = []
#     async for green in bouquet.greenery.all():
#         greeneries.append(f'{green.name}')
#     greenery = ''.join(greeneries)
#     await callback.answer(
#         text=f'Состав букета:\n\n'
#         f'{flowers}\n{greenery}',
#         show_alert=True,
#     )



@router.message(Command(commands=['order']))
async def show_start_order(message: Message):
    await bot.send_message(message.from_user.id, 'Заказы 🗒', reply_markup=order_main_menu)


@router.message(F.text == "главное меню")
async def show_start_order(message: Message):
    await bot.send_message(message.from_user.id, 'переход в основное меню бота...', reply_markup=order_main_menu)


@router.message(F.text == "Посмотреть заказы")
async def show_order(message: Message):
    await bot.send_message(message.from_user.id, "🗒", reply_markup=order_choise)


@router.message(F.text.lower() == "меню заказов")
async def order_menu(message: Message):
    await bot.send_message(message.from_user.id, '🗒', reply_markup=order_main_menu)

@router.message(F.text.lower() == "посмотреть все 📊")
async def order_view_all(message: Message):
    await bot.send_message(message.from_user.id, '🗒', reply_markup=order_main_menu)
    full_order = []
    async for order in Order.objects.all().order_by('status'):
        full_order.append(f'Статус {order.status}\nАдрес доставки : {order.delivery_address} - {order.delivery_date}\nКонтактное лицо {order.contact_name} т.{order.contact_phone}\n\n')
    orders = ''.join(full_order)
    await message.answer(f'Перечень заказов!\n\n{orders}')

@router.message(F.text.lower() == "только новые 🆕")
async def order_new_only(message: Message):
    await bot.send_message(message.from_user.id, '🗒', reply_markup=order_main_menu)
    full_order = []
    async for order in Order.objects.filter(status='new').order_by('delivery_date'):
        full_order.append(f'Статус {order.status}\nАдрес доставки : {order.delivery_address} - {order.delivery_date}\nКонтактное лицо {order.contact_name} т.{order.contact_phone}\n\n')
    orders = ''.join(full_order)
    await message.answer(f'Перечень заказов!\n\n{orders}')

@router.message(F.text.lower() == "изменить статус заказа")
async def change_order_type(message: Message):
    await bot.send_message(message.from_user.id, "🗒 - укажите тип заказа для смены статуса", reply_markup=order_change_type)

@router.message(F.text.startswith('*'))
async def get_new_order_id(message: Message):
    id = message.text.split('-')[-1].replace('[','').replace(']','')
    await bot.send_message(message.from_user.id, f"id заказа для смены статуса {id}", reply_markup=order_main_menu)
    # DO: по id изменить в БД вид заказа на следующий т.е. новый-


@router.message(F.text.lower() == "new - новый")
async def change_new_type(message: Message):
    builder = ReplyKeyboardBuilder()
    async for order in Order.objects.filter(status='new').order_by('delivery_date'):
        builder.add(types.KeyboardButton(text=f"*{order.contact_name}-{order.contact_phone}-[{order.id}]", callback_data="*"))
    builder.adjust(1)

    await message.answer("Выберите клиента:",reply_markup=builder.as_markup(resize_keyboard=True))

# @router.callback_query(F.data.startswith('*'))
# async def send_random_value(callback: types.CallbackQuery):
#     await callback.message.answer("str(randint(1, 10))")

# async def get_order_id(callback: types.CallbackQuery):


