from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from django.core.management import BaseCommand
from shopbot.management.commands.bot import user_handlers

import conf.settings as settings

TG_BOT_API: str = settings.TG_BOT_API

bot: Bot = Bot(token=TG_BOT_API, parse_mode='HTML')
dp: Dispatcher = Dispatcher()

dp.include_router(user_handlers.router)


class Command(BaseCommand):
    def handle(self, *args, **options):
        dp.run_polling(bot)
