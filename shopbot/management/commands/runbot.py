from aiogram import Bot, Dispatcher
from django.core.management import BaseCommand

import conf.settings as settings
from shopbot.management.commands.bot import user_handlers
from environs import Env
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d - %(levelname)-8s - %(asctime)s - %(funcName)s - %(name)s - %(message)s'
    )

logger = logging.getLogger(__name__)

env: Env = Env()
env.read_env()

bot: Bot = Bot(token=env('TG_BOT_API'), parse_mode='HTML')
dp: Dispatcher = Dispatcher()

dp.include_router(user_handlers.router)


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info('Bot started')
        dp.run_polling(bot)
