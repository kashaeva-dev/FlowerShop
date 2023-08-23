from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from shopbot.management.commands.bot.user_keyboards import give_buttons_with_occasion, give_buttons_with_prices
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StatesGroup, State

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


@router.callback_query(F.data == 'цена')
async def handle_prices(callback: CallbackQuery):
    await callback.message.answer('На какую сумму рассчитываете?', reply_markup=await give_buttons_with_prices())
