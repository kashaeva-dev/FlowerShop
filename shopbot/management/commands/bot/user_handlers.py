from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from shopbot.management.commands.bot.user_keyboards import give_buttons_with_occasion, give_buttons_with_prices
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StatesGroup, State

import logging
import os

from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.filters import Command
from aiogram import F
from asgiref.sync import sync_to_async
from environs import Env

from conf.settings import BASE_DIR
from shopbot.models import Client, Advertisement, Staff, Bouquet
from shopbot.management.commands.bot.user_keyboards import get_catalog_keyboard


logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d - %(levelname)-8s - %(asctime)s - %(funcName)s - %(name)s - %(message)s'
    )

logger = logging.getLogger(__name__)


env: Env = Env()
env.read_env()

bot: Bot = Bot(token=env('TG_BOT_API'), parse_mode='HTML')


router = Router()


class OrderOccasion(StatesGroup):
    name_occasion = State()


@router.message(Command(commands=["start"]))
async def start_command_handler(message: Message):
    await message.answer('К какому событию готовимся? Выберите один из вариантов, либо укажите свой',
                         reply_markup=await give_buttons_with_occasion())


@router.callback_query(F.data == 'какой повод')
async def handle_another_occasion(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Укажите повод для заказа букета', reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderOccasion.name_occasion)



@router.message(OrderOccasion.name_occasion)
async def handle_price_another_occasion(mess: Message):
    await mess.answer('На какую сумму рассчитываете?', reply_markup=await give_buttons_with_prices())

    client, created = await sync_to_async(Client.objects.get_or_create)(telegram_id=user_id)



@router.callback_query(F.data == 'цена')
async def handle_prices(callback: CallbackQuery):
    await callback.message.answer('На какую сумму рассчитываете?', reply_markup=await give_buttons_with_prices())


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

