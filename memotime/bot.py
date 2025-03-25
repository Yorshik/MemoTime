import asyncio
import logging
import os
import sys

import aiogram.filters
import aiogram.fsm.state
import aiogram.fsm.context
import decouple
import django
from asgiref.sync import sync_to_async
from django.utils.translation import gettext_lazy as _

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "memotime.settings")
django.setup()

import apps.users.models as users_models


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

bot = aiogram.Bot(token=decouple.config("MEMOTIME_BOT_TOKEN"))
dp = aiogram.Dispatcher()
router = aiogram.Router()


class LogoutState(aiogram.fsm.state.StatesGroup):
    waiting_for_confirmation = aiogram.fsm.state.State()


class LoginState(aiogram.fsm.state.StatesGroup):
    waiting_for_username = aiogram.fsm.state.State()
    waiting_for_password = aiogram.fsm.state.State()


async def send_telegram_message(chat_id, message):
    await bot.send_message(chat_id, message)


@sync_to_async
def get_user_async(data, criteria):
    try:
        if criteria == "username":
            return users_models.User.objects.get(username=data.lower())
        elif criteria == "telegram_id":
            return users_models.User.objects.get(telegram_id=data)
    except users_models.User.DoesNotExist:
        return None


@sync_to_async
def save_user_async(user):
    user.save()


@router.message(aiogram.filters.Command("start"))
async def start_command(message: aiogram.types.Message):
    await message.reply(
        str(
            _(
                """
Hey there!
I'm the MemoTime bot, your personal notification assistant.
I'll make sure you never miss an important event—just connect your account, and I'll send you reminders right here.
Need more info? Type /help.
"""
            )
        )
    )


@router.message(aiogram.filters.Command("help"))
async def help_command(message: aiogram.types.Message):
    await message.reply(
        str(
            _(
                """
Help Menu
Here are the available commands:
/login – Log in to your MemoTime account. After using this command, enter your username first, then send your password in the next message.
/logout – Log out of your account.
That's all for now.
""",
            ),
        ),
    )


@router.message(aiogram.filters.Command("login"))
async def start_login(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
):
    await message.answer(str(_("Enter your username:")))
    await state.set_state(LoginState.waiting_for_username)


@router.message(LoginState.waiting_for_username)
async def process_username(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
):
    await state.update_data(username=message.text)
    await message.answer(str(_("Enter your password:")))
    await state.set_state(LoginState.waiting_for_password)


@router.message(LoginState.waiting_for_password)
async def process_password(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
):
    user_data = await state.get_data()
    username = user_data.get("username")
    password = message.text

    if await authenticate_user(message, username, password):
        await message.answer(str(_("Login successful!")))
    else:
        await message.answer(str(_("Invalid credentials. Try again.")))

    await state.clear()


async def authenticate_user(
    message: aiogram.types.Message,
    username: str,
    password: str,
) -> bool:
    user = await get_user_async(username, "username")
    if not user:
        return False

    if user.check_password(password):
        user.is_telegram_subscribed = True
        user.telegram_id = message.from_user.id
        await save_user_async(user)
        return True

    return False


@router.message(aiogram.filters.Command("logout"))
async def logout_start(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
):
    await state.set_state(LogoutState.waiting_for_confirmation)
    await message.answer(
        str(_("Are you sure you want to quit? Type 'yes' for confirmation")),
    )


@router.message(
    LogoutState.waiting_for_confirmation,
    lambda msg: msg.text.lower() in ["да", "yes"],
)
async def confirm_logout(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
):
    user = await get_user_async(message.from_user.id, "telegram_id")
    if not user:
        await message.answer(
            str(_("Logout failed. Maybe you have already logged out?")),
        )

        return

    user.is_telegram_subscribed = False
    user.telegram_id = None
    await save_user_async(user)
    await message.answer(str(_("Logout is successful")))
    await state.clear()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
