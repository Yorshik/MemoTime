import os
import decouple
import django
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from asgiref.sync import sync_to_async
from django.utils.translation import gettext_lazy as _

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "memotime.settings")
django.setup()

from apps.users.models import User

bot = Bot(decouple.config("MEMOTIME_BOT_TOKEN"))
dp = Dispatcher()

GREETINGS = {
    "en-us": "Hello, {username}. I'm here to send you some notifications.",
    "ru-ru": "Привет, {username}. Я здесь чтобы отправлять тебе напоминания",
}


async def send_telegram_message(chat_id, message):
    await bot.send_message(chat_id, message)


@sync_to_async
def link_user(telegram_id, username):
    try:
        user = User.objects.get(username=username.lower())
        user.is_telegram_subscribed=True
        user.telegram_id=telegram_id
        user.save()
        return True
    except User.DoesNotExist:
        return False


@dp.message(Command("start"))
async def start_command(message, command):
    args = command.args
    if not args or "_" not in args:
        await message.reply("Not correct")
        return
    username, lang = args.split("_", 1)
    if lang not in "en-usru-ru":
        await message.reply("Not correct")
        return
    if await link_user(message.from_user.id, username):
        await message.reply(GREETINGS[lang].format(username=username))
    else:
        await message.reply("Error: user not found")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

