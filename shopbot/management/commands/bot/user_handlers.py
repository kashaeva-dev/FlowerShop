import pytz as pytz
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StatesGroup, State

import logging
import os
import datetime

from aiogram import Router, Bot, types
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.filters import Command
from aiogram import F
from asgiref.sync import sync_to_async
from environs import Env

from conf.settings import BASE_DIR
# from shopbot.models import Client, Advertisement, Staff, Bouquet, Order
from shopbot.management.commands.bot.user_keyboards import get_catalog_keyboard, get_main_menu, to_main_menu
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from shopbot.management.commands.bot.user_menu import main_menu, order_main_menu, order_choise, order_change_type
from shopbot.models import (
    Client,
    Staff,
    Order,
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

file_handler = logging.FileHandler(f'{BASE_DIR}/botlog.txt', mode='w')

logger = logging.getLogger(__name__)
logger.addHandler(file_handler)

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
    telegram_id = message.from_user.id

    await bot.send_message(message.from_user.id, 'Вас приветствует бот-флорист',
                           reply_markup= await get_main_menu(telegram_id))


@router.callback_query(F.data == 'main_menu')
async def main_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('ГЛАВНОЕ МЕНЮ:',
                                     reply_markup=await get_main_menu(callback.from_user.id))


@router.callback_query(F.data == 'FAQ')
async def FAQ_handler(callback: CallbackQuery):
    await callback.message.edit_text('<b>FLOWER SHOP</b>\n\n'
                                     'Закажите доставку праздничного букета,'
                                     ' собранного специально для ваших любимых,'
                                     ' родных и коллег. Наш букет со смыслом'
                                     ' станет главным подарком на вашем празднике!\n\n'
                                     '<b>Адреса салонов:</b>\n'
                                     '1. Красноярск, ул. Лесная, д.3\n'
                                     '2. Красноярск, ул. Праздничная, д18\n\n'
                                     '<b>Телефон:</b> 888-88-88',
                                     reply_markup=await to_main_menu())


@router.callback_query(F.data == 'start_order')
async def start_order_handler(callback: CallbackQuery):
    await callback.message.edit_text('К какому событию готовимся? Выберите один из вариантов, либо укажите свой',
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
    await state.clear()
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


@router.callback_query(F.data == 'catalog')
async def show_start_catalog_handler(message: Message):
    logger.info(f'start catalog handler')
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


@router.callback_query(F.data == "currier")
async def show_start_order(message: Message):
    await bot.send_message(message.from_user.id, 'Заказы 🗒', reply_markup=order_main_menu)


@router.message(F.text == "Главное меню")
async def show_main_menu(message: Message):
    await bot.send_message(message.from_user.id, 'и снова привет от бота...', reply_markup=main_menu)

@router.message(F.text == "Оформить заказ")
async def create_order(message: Message):
    await message.answer('К какому событию готовимся? Выберите один из вариантов, либо укажите свой',
                         reply_markup=await get_occasions_keyboard())

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

@router.message(F.text == "Cтатусы заказов (изменение)")
async def change_order_type(message: Message):
    await bot.send_message(message.from_user.id, "🗒 - укажите тип заказа для смены статуса", reply_markup=order_change_type)

@router.message(F.text.startswith('*'))
async def get_new_order_id(message: Message):
    id = message.text.split('-')[-1].replace('[','').replace(']','')
    await bot.send_message(message.from_user.id, "Укажите (при наличии) клиента для смены статуса", reply_markup=order_main_menu)
    await sync_to_async(Order.objects.filter(pk=id).update)(status="processing")

@router.message(F.text.startswith('@'))
async def get_new_order_id(message: Message):
    id = message.text.split('-')[-1].replace('[','').replace(']','')
    await bot.send_message(message.from_user.id, "Укажите (при наличии) клиента для смены статуса - Доставлен", reply_markup=order_main_menu)
    await sync_to_async(Order.objects.filter(pk=id).update)(status="delivered")

@router.message(F.text.startswith('!'))
async def get_new_order_id(message: Message):
    id = message.text.split('-')[-1].replace('[','').replace(']','')
    await bot.send_message(message.from_user.id, "Укажите (при наличии) клиента для смены статуса - Отменен", reply_markup=order_main_menu)
    await sync_to_async(Order.objects.filter(pk=id).update)(status="canceled")


@router.message(F.text == "Принять 'Новый' в работу")
async def change_new_type(message: Message):
    builder = ReplyKeyboardBuilder()
    async for order in Order.objects.filter(status='new').order_by('delivery_date'):
        builder.add(types.KeyboardButton(text=f"*{order.contact_name}\nт.{order.contact_phone}-[{order.id}]", callback_data="*"))
    builder.adjust(1)
    await message.answer("Выберите клиента:",reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(F.text == "Указать - Доставлен")
async def change_new_type(message: Message):
    builder = ReplyKeyboardBuilder()
    async for order in Order.objects.filter(status='processing').order_by('delivery_date'):
        builder.add(types.KeyboardButton(text=f"@{order.contact_name}\nт.{order.contact_phone}-[{order.id}]", callback_data="@"))
    builder.adjust(1)
    await message.answer("Выберите клиента которому доставлен заказ",reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(F.text == "Указать - Отменен")
async def change_new_type(message: Message):
    builder = ReplyKeyboardBuilder()
    async for order in Order.objects.filter(status='processing').order_by('delivery_date'):
        builder.add(types.KeyboardButton(text=f"!{order.contact_name}\nт.{order.contact_phone}-[{order.id}]", callback_data="!"))
    builder.adjust(1)
    await message.answer("Выберите клиента у которого отменен заказ",reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(F.text == "Заказы - В работе")
async def change_new_type(message: Message):
    builder = ReplyKeyboardBuilder()
    async for order in Order.objects.filter(status='processing').order_by('delivery_date'):
        builder.add(types.KeyboardButton(text=f"#{order.contact_name}\nт.{order.contact_phone}-[{order.id}]", callback_data="#"))
    builder.adjust(1)
    await message.answer("Заказы в работе\nУкажите клиента для подробной информации",reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(F.text.startswith('#'))
async def get_new_order_id(message: Message):
    id = message.text.split('-')[-1].replace('[','').replace(']','')
    await bot.send_message(message.from_user.id, f"Укажите клиента (при наличии) для детализации заказа", reply_markup=order_main_menu)
    order_detail = await sync_to_async(Order.objects.filter(pk=id).first)()
    await message.answer(f"Заказ клиента №"
                         f"{order_detail.id} Статус [{order_detail.status}]\n"
                         f"Создан {order_detail.created_at}. Дата доставки {order_detail.delivery_date}\n"
                         f"{order_detail.delivery_address} {order_detail.contact_phone} {order_detail.contact_name}")


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
    logger.info(f'start_order: {bouquet}')
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
    await message.answer('⏰ Укажите дату и время доставки в формате <b>ДД.ММ.ГГГГ ЧЧ:ММ</b>',
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
    order_data = await state.get_data()
    client, _ = await sync_to_async(Client.objects.get_or_create)(telegram_id=message.from_user.id,
                                                                  first_name=order_data['user_name'])
    bouquet = await sync_to_async(Bouquet.objects.get)(pk=order_data['bouquet'])
    logger.info(f'{client}')
    await state.update_data(client=client)
    delivery_date = datetime.datetime.strptime(order_data['date'], '%d.%m.%Y %H:%M')
    delivery_date = delivery_date.astimezone(pytz.timezone('Europe/Moscow'))
    new_order = await sync_to_async(Order.objects.create)(
        client=client,
        bouquet=bouquet,
        delivery_date=delivery_date,
        delivery_address=order_data['adress'],
        contact_phone=order_data['phonenumber'],
        contact_name=order_data['user_name'],
        status='new',
    )
    await message.answer(
        text='Спасибо, за заказ 👍!\n\n'
             f'Номер Вашего заказа <b>№{new_order.pk}</b>. Наш курьер свяжется с Вами в ближайшее время!\n\n'
             '<b>Хотите что-то еще более уникальное? '
             'Подберите другой букет из нашей коллекции или закажите консультацию флориста</b>',
        reply_markup=await get_order_keybord(),
        parse_mode='HTML'
    )
    await state.clear()

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
