from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
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
from shopbot.models import (
    Client,
    Advertisement,
    Staff,
    Bouquet,
    FlowerComposition,
    GreeneryComposition,
    Occasion,
)
from shopbot.management.commands.bot.user_keyboards import (
    get_catalog_keyboard,
    get_occasions_keyboard,
    get_price_ranges_keyboard,
    get_order_keybord
)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d - %(levelname)-8s - %(asctime)s - %(funcName)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

env: Env = Env()
env.read_env()

bot: Bot = Bot(token=env('TG_BOT_API'), parse_mode='HTML')

router = Router()


class Order(StatesGroup):
    user_occasion = State()
    user_name = State()
    user_adress = State()
    user_date_time_order = State()
    user_phonenumber_order = State()
    user_phonenumber_consultation = State()


@router.message(Command(commands=["start"]))
async def start_command_handler(message: Message):
    await message.answer('К какому событию готовимся? Выберите один из вариантов, либо укажите свой',
                         reply_markup=await get_occasions_keyboard())


@router.callback_query(F.data.startswith('occasion_'))
async def get_occasion_handler(callback: CallbackQuery, state: FSMContext):
    logger.info(f'start occasion handler - {callback.data}')
    occasion = callback.data.split('_')[-1]
    if occasion == '10':
        await callback.message.answer('В ответном сообщении напишите свой повод для заказа букета',
                                      reply_markup=ReplyKeyboardRemove()
                                      )
        await state.set_state(Order.user_occasion)
    else:
        await state.update_data(occasion=occasion, user_occasion=None)
        await callback.message.answer('На какую сумму рассчитываете?',
                                      reply_markup=await get_price_ranges_keyboard())


@router.message(Order.user_occasion)
async def get_user_occasion_handler(message: Message, state: FSMContext):
    await state.update_data(occasion='10', user_occasion=message.text)
    await message.answer('На какую сумму рассчитываете?',
                         reply_markup=await get_price_ranges_keyboard())

@router.callback_query(F.data.startswith == 'price_')
async def get_price_range_handler(callback: CallbackQuery):
    await callback.message.answer('На какую сумму рассчитываете?',
                                  reply_markup=await get_price_ranges_keyboard())



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


@router.callback_query(F.data.startswith('show_composition_'))
async def show_composition_handler(callback: CallbackQuery):
    bouquet_id = callback.data.split('_')[-1]
    bouquet = await sync_to_async(Bouquet.objects.filter(pk=bouquet_id)
                                  .first)()
    composition_flowers = await sync_to_async(FlowerComposition.objects.select_related('flower')
                                              .filter)(bouquet=bouquet)
    flowers = []
    async for composition_flower in composition_flowers:
        flowers.append(f'{composition_flower.flower.name} - {composition_flower.quantity} шт.\n')
    flowers = ''.join(flowers)
    composition_greeneries = await sync_to_async(GreeneryComposition.objects.select_related('greenery')
                                                 .filter)(bouquet=bouquet)
    greeneries = []
    async for composition_greenery in composition_greeneries:
        greeneries.append(f'{composition_greenery.greenery.name} - {composition_greenery.quantity} шт./упак.\n')
    greeneries = ''.join(greeneries)
    image_path = os.path.join(BASE_DIR, bouquet.image.url.lstrip('/'))
    logger.info(f'picture path {image_path}')
    photo = FSInputFile(image_path)
    await bot.edit_message_media(chat_id=callback.from_user.id,
                                 message_id=callback.message.message_id,
                                 media=InputMediaPhoto(media=photo,
                                                       caption=f'{bouquet.name.upper()}\n\n'
                                                               f'<b>🌹 Состав букета</b>:\n\n'
                                                               f'{flowers}\n{greeneries}\n'
                                                               f'Упаковка - {bouquet.wrapping}\n\n'
                                                               f'<b>💰 {bouquet.price} руб.</b>'),
                                 reply_markup=await get_catalog_keyboard(bouquet.id)
                                 )


@router.callback_query(F.data == 'start_order')
async def show_order_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Order.user_name)
    await callback.message.answer('👤 Укажите Ваше имя',
                                  reply_markup=ReplyKeyboardRemove()
                                  )


@router.message(Order.user_name)
async def show_adress_handler(message: Message, state: FSMContext):
    await state.set_state(Order.user_adress)
    await message.answer('🏠 Укажите Ваш адрес',
                         reply_markup=ReplyKeyboardRemove()
                         )


@router.message(Order.user_adress)
async def show_datetime_handler(message: Message, state: FSMContext):
    await state.set_state(Order.user_date_time_order)
    await message.answer('⏰ Укажите дату и время доставки',
                         reply_markup=ReplyKeyboardRemove()
                         )


@router.message(Order.user_date_time_order)
async def show_phonenumber_handler(message: Message, state: FSMContext):
    await state.set_state(Order.user_phonenumber_order)
    await message.answer('📲 Укажите Ваш номер телефона',
                         reply_markup=ReplyKeyboardRemove()
                         )


@router.message(Order.user_phonenumber_order)
async def show_phonenumber_handler(message: Message):
    await message.answer(
        text='Спасибо, за заказ 👍 Наш курьер свяжется с Вами в ближайшее время!\n\n'
             '<b>Хотите что-то еще более уникальное? '
             'Подберите другой букет из нашей коллекции или закажите консультацию флориста</b>',
        reply_markup=await get_order_keybord(),
        parse_mode='HTML'
    )


@router.callback_query(F.data == 'all_bouquets')
async def show_all_bouquets_handler(callback: CallbackQuery):
    bouquet = await sync_to_async(Bouquet.objects.all().first)()
    image_path = os.path.join(BASE_DIR, bouquet.image.url.lstrip('/'))
    logger.info(f'picture path {image_path}')
    photo = FSInputFile(image_path)
    await bot.send_photo(
        chat_id=callback.from_user.id,
        caption=f'{bouquet.name.upper()}\n\n'
                f'<b>💡 Смысл букета</b>:\n\n{bouquet.meaning}\n\n'
                f'<b>💰 {bouquet.price} руб.</b>',
        photo=photo,
        reply_markup=await get_catalog_keyboard(bouquet.id)
    )


@router.callback_query(F.data == 'consultation')
async def show_consultation_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Order.user_phonenumber_consultation)
    await callback.message.answer('📲 Укажите номер телефона, и наш флорист перезвонит Вами в течение 20 минут!',
                                  reply_markup=ReplyKeyboardRemove()
                                  )


@router.message(Order.user_phonenumber_consultation)
async def show_phonenumber_consultation_handler(message: Message):
    await message.answer(
        text='Флорист скоро свяжется с вами!\n\n'
             'А пока можете присмотреть что-нибудь из готовой коллекции ☝️',
        reply_markup=await show_all_bouquets_handler(message))
