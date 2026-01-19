import asyncio
import os
import json
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
import gspread
from google.oauth2.service_account import Credentials

BOT_TOKEN = os.getenv("BOT_TOKEN")  # env в Pella
GOOGLE_SHEETS_KEY = os.getenv("GOOGLE_SHEETS_KEY")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
creds_dict = json.loads(GOOGLE_CREDS_JSON)

BOOKS = {
    "book1": {"name": "Йога для начинающих", "price": 500},
    "book2": {"name": "Медитация", "price": 700},
}

SBP_QR_LINK_TEMPLATE = os.getenv("SBP_QR_LINK_TEMPLATE")

# Google Sheets (твой creds_dict)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(GOOGLE_SHEETS_KEY).sheet1

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    parts = message.text.split()
    if len(parts) > 1:
        payload = parts[1]
        book_id, amount_str = payload.split("_")
        book = BOOKS.get(book_id)
        if book:
            amount_cents = int(amount_str) * 100
            sbp_link = SBP_QR_LINK_TEMPLATE

            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Оплатить по СБП", url=sbp_link)],
                [InlineKeyboardButton(text="Я оплатил", callback_data=f"paid_{payload}")]
            ])
            
            await message.answer(
                f"<b>{book['name']}</b>\n"
                f"💰 <b>{amount_str} ₽</b>\n\n"
                f"💳 <b>Ссылка Сбер Online:</b>\n{sbp_link}\n"
                f"📱 <b>ИЛИ СБП перевод:</b>\n"
                f"Получатель: <b>К. Сергей</b>\n"
                f"Карта Тинькофф: <b>+7 911 313-41-99</b>\n\n"
                f"После оплаты нажми «Я оплатил» ✅",
                reply_markup=kb,
                parse_mode="HTML"
            )    

        else:
            await message.answer("Книга не найдена.")
    else:
        await message.answer("Привет! Сканируй QR-код на книге.")

@dp.callback_query(F.data.startswith("paid_"))
async def paid_handler(callback: CallbackQuery):
    payload = callback.data[len("paid_"):]  # "book1_500"
    book_id, amount_str = payload.split("_")
    book = BOOKS.get(book_id)
    
    # ЗАПИСЬ В ТАБЛИЦУ!
    sheet.append_row([
        callback.from_user.username or str(callback.from_user.id),
        book["name"] if book else book_id,
        amount_str,
        str(callback.message.date)
    ])
    
    await callback.message.edit_text(
        f"✅ <b>Спасибо за покупку {book['name'] if book else book_id}!</b>\n"
        f"Сумма: {amount_str} ₽\n"
        f"Запись добавлена в учёт."
    )
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

