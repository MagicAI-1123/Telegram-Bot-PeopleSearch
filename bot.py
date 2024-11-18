import asyncio
import logging

from aiogram.client.default import DefaultBotProperties

from handlers.start import start_router
from handlers.photo import photo_router
from handlers.email import email_router
from handlers.phone import phone_router
from handlers.fullname import fullname_router
from handlers.skype import skype_router
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# async def periodic():
#     while True:
#         print('sdfdsfsdf')
#         await asyncio.sleep(5)
            
async def main() -> None:
    dp = Dispatcher()
    dp.include_routers(
        start_router,
        fullname_router,
        email_router,
        phone_router,
        skype_router
    )

    # asyncio.create_task(periodic())

    session = AiohttpSession()

    # Initialize bot with proxy
    bot = Bot(TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
