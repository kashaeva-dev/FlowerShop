from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StatesGroup, State

import logging
import os
import datetime

from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.filters import Command
from aiogram import F
from asgiref.sync import sync_to_async
from environs import Env

from conf.settings import BASE_DIR
from shopbot.models import (
    Client,
    Staff,
    Bouquet,
    FlowerComposition,
    GreeneryComposition,
    Occasion,
    Order,
    Consulting,
)
from shopbot.management.commands.bot.user_keyboards import (
    get_catalog_keyboard,
    get_occasions_keyboard,
    get_price_ranges_keyboard,
    get_order_keybord,
    get_bouquet_keyboard
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


class OrderState(StatesGroup):
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
        await state.set_state(OrderState.user_occasion)
    else:
        await state.update_data(occasion=occasion, user_occasion=None)
        await callback.message.answer('На какую сумму рассчитываете?',
                                      reply_markup=await get_price_ranges_keyboard())


@router.message(OrderState.user_occasion)
async def get_user_occasion_handler(message: Message, state: FSMContext):
    await state.update_data(occasion='10', user_occasion=message.text)
    await message.answer('На какую сумму рассчитываете?',
                         reply_markup=await get_price_ranges_keyboard())


@router.callback_query(F.data.startswith('price_'))
async def get_price_range_handler(callback: CallbackQuery, state: FSMContext):
    bouquet_occasions = await state.get_data()
    bouquet_occasion = int(bouquet_occasions['occasion'])
    bouquet_price = int(callback.data.split('_')[-1])
    bouquets = await sync_to_async(Bouquet.objects.filter)(occasion__pk__in=[bouquet_occasion], price__lt=bouquet_price)
    async for bouquet in bouquets:
        image_path = os.path.join(BASE_DIR, bouquet.image.url.lstrip('/'))
        logger.info(f'picture path {image_path}')
        logger.info(f'{bouquet.name}')
        photo = FSInputFile(image_path)

        await bot.send_photo(
            chat_id=callback.from_user.id,
            caption=f'{bouquet.name.upper()}\n\n'
                    f'<b>💡 Смысл букета</b>:\n\n{bouquet.meaning}\n\n'
                    f'<b>💰 {bouquet.price} руб.</b>',
            photo=photo,
            reply_markup=await get_bouquet_keyboard(bouquet.pk)
        )


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


@router.callback_query(F.data.startswith('show_occasion_composition_'))
async def show_composition_occasion_handler(callback: CallbackQuery):
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
                                 reply_markup=await get_bouquet_keyboard(bouquet.id)
                                 )


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


@router.callback_query(F.data.startswith('start_order_'))
async def show_order_handler(callback: CallbackQuery, state: FSMContext):
    bouquet = int(callback.data.split('_')[-1])
    await state.set_state(OrderState.user_name)
    await callback.message.answer('👤 Укажите Ваше имя',
                                  reply_markup=ReplyKeyboardRemove()
                                  )
    await state.update_data(bouquet=bouquet)


@router.message(OrderState.user_name)
async def show_adress_handler(message: Message, state: FSMContext):
    await state.set_state(OrderState.user_adress)
    await message.answer('🏠 Укажите Ваш адрес',
                         reply_markup=ReplyKeyboardRemove()
                         )
    await state.update_data(user_name=message.text)


@router.message(OrderState.user_adress)
async def show_datetime_handler(message: Message, state: FSMContext):
    await state.set_state(OrderState.user_date_time_order)
    await message.answer('⏰ Укажите дату и время доставки',
                         reply_markup=ReplyKeyboardRemove()
                         )
    await state.update_data(adress=message.text)


@router.message(OrderState.user_date_time_order)
async def show_phonenumber_handler(message: Message, state: FSMContext):
    await state.set_state(OrderState.user_phonenumber_order)
    await message.answer('📲 Укажите Ваш номер телефона',
                         reply_markup=ReplyKeyboardRemove()
                         )
    logger.info(f'{message.text}')
    await state.update_data(date=message.text)


@router.message(OrderState.user_phonenumber_order)
async def show_phonenumber_handler(message: Message, state: FSMContext):
    await state.update_data(phonenumber=message.text)
    await message.answer(
        text='Спасибо, за заказ 👍 Наш курьер свяжется с Вами в ближайшее время!\n\n'
             '<b>Хотите что-то еще более уникальное? '
             'Подберите другой букет из нашей коллекции или закажите консультацию флориста</b>',
        reply_markup=await get_order_keybord(),
        parse_mode='HTML'
    )
    order_data = await state.get_data()
    client, _ = await sync_to_async(Client.objects.get_or_create)(telegram_id=message.from_user.id,
                                                                  first_name=order_data['user_name'])
    bouquet = await sync_to_async(Bouquet.objects.get)(pk=order_data['bouquet'])
    logger.info(f'{client}')
    await state.update_data(client=client)
    await sync_to_async(Order.objects.create)(
        client=client,
        bouquet=bouquet,
        delivery_date=datetime.datetime.strptime(order_data['date'], '%d.%m.%Y %H:%M'),
        delivery_address=order_data['adress'],
        contact_phone=order_data['phonenumber'],
        contact_name=order_data['user_name']
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
    await state.set_state(OrderState.user_phonenumber_consultation)
    await callback.message.answer('📲 Укажите номер телефона, и наш флорист перезвонит Вами в течение 20 минут!',
                                  reply_markup=ReplyKeyboardRemove()
                                  )


@router.message(OrderState.user_phonenumber_consultation)
async def show_phonenumber_consultation_handler(message: Message, state: FSMContext):
    await state.update_data(user_phonenumber_consultation=message.text)
    consultation_data = await state.get_data()
    florist = await sync_to_async(Staff.objects.filter(role='florist').order_by("?").first)()
    occasion = await sync_to_async(Occasion.objects.get)(
        pk=int(consultation_data['occasion']) if 'occasion' in consultation_data else 10)
    client, _ = await sync_to_async(Client.objects.get_or_create)(telegram_id=message.from_user.id,
                                                                  first_name=consultation_data[
                                                                      'user_name'] if 'user_name' in consultation_data else None)
    consultation = await sync_to_async(Consulting.objects.create)(
        client=client,
        florist=florist,
        contact_phone=consultation_data['user_phonenumber_consultation'],
        occasion=occasion
    )
    if 'occasion' in consultation_data:
        await sync_to_async(Order.objects.last().update)(consultation=consultation)
    await message.answer(
        text=f'Флорист <i><b>{florist.first_name}</b></i> скоро свяжется с вами!\n\n'
             'А пока можете присмотреть что-нибудь из готовой коллекции ☝️',
        reply_markup=await show_all_bouquets_handler(message), parse_mode='HTML')
