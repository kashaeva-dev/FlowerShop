from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from asgiref.sync import sync_to_async

from shopbot.models import Client, Advertisement, Staff

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

