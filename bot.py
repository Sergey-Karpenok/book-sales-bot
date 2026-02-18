import asyncio
import os
import json
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
import gspread
from google.oauth2.service_account import Credentials
from aiogram import Router

BOT_TOKEN = os.getenv("BOT_TOKEN")  # env в Pella
GOOGLE_SHEETS_KEY = os.getenv("GOOGLE_SHEETS_KEY")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
creds_dict = json.loads(GOOGLE_CREDS_JSON)

BOOKS = {
    "book1": {"name": "Фундаментальная философия", "price": 550},
    "book2": {"name": "Чарьячарья 1", "price": 200},
    "book3": {"name": "Чарьячарья 2", "price": 200},
    "book4": {"name": "Чарьячарья 3", "price": 400},
    "book5": {"name": "Ананда Вани самграха", "price": 200},
    "book6": {"name": "Ананда Вачанамритам. Ч. 1-2", "price": 350},
    "book7": {"name": "Мысли П.Р. Саркара", "price": 350},
    "book8": {"name": "Дживан веда (Руководство к поведению человека) ", "price": 300},
    "book9": {"name": "102 прабхат самгита (двухтомник) Том №1", "price": 500},
    "book10": {"name": "102 прабхат самгита (двухтомник) Том №2", "price": 500},
    "book11": {"name": "Неогуманизм: освобождение интеллекта", "price": 400},
    "book12": {"name": "Пища для мыслей", "price": 200},
    "book13": {"name": "Уроки медитации", "price": 350},
    "book14": {"name": "Комментарии к Ананда сутрам", "price": 750},
    "book15": {"name": "За пределами сверхсознания", "price": 350},
    "book16": {"name": "Путь Блаженства", "price": 200},
    "book17": {"name": "Путешествие с мистическим мастером", "price": 800},
    "book18": {"name": "Шаранагати", "price": 700},
    "book19": {"name": "Праутистская экономика", "price": 800},
    "book20": {"name": "Анандамурти: годы в Джамалпуре", "price": 1100},
    "book21": {"name": "Беседы о неогуматистическом образовании", "price": 800},
    "book22": {"name": "Лисьи огни", "price": 400},
    "book23": {"name": "Намах Шивая шантая", "price": 550},
    "book24": {"name": "Чарьячарья 1 (старая)", "price": 150},
    "book25": {"name": "Чарьячарья 2 (старая)", "price": 150},
    "book26": {"name": "Беседы о тантре, ч.1", "price": 700},
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
            sbp_link = SBP_QR_LINK_TEMPLATE.format(amount=amount_cents)

            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💳 Оплатить по СБП", url=sbp_link)],  # иконка 💳
                [InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"paid_{payload}")]
            ])

            # await message.answer(
            #     f"*{book['name']}*\n"
            #     f"💰 *{amount_str} ₽*\n\n"
            #     f"📱 *Для ручного СБП перевода\\:*\n"
            #     f"*Получатель\\: К\\. Сергей*\n"
            #     f"*Карта Тинькофф\\:*\n"
            #     "`+7 911 313-41-99`\n\n"
            #     f"*После оплаты нажми \\«Я оплатил\\» ✅*",
            #     reply_markup=kb,
            #     parse_mode="MarkdownV2"
            # )

            await message.answer(
                f"<b>{book['name']}</b>\n"
                f"💰 <b>{amount_str} ₽</b>\n\n"
                f"📱 <b>Для ручного СБП перевода:</b>\n"
                f"<b>Получатель: К. Сергей</b>\n"
                f"<b>Карта Тинькофф:</b>\n"
                f"<code>+7 911 313-41-99</code>\n\n"
                f"<b>После оплаты нажми «Я оплатил» ✅</b>",
                reply_markup=kb,
                parse_mode="HTML"
            )
            
            # await message.answer(
            #     f"<b>{book['name']}</b>\n"
            #     f"💰 <b>{amount_str} ₽</b>\n\n"
            #     f"📱 <b>Для ручного СБП перевода:</b>\n"
            #     f"Получатель: <b>К. Сергей</b>\n"
            #     f"Карта Тинькофф: <b>+7 911 313-41-99</b>\n\n"
            #     f"Телефон можно скопировать в сообщении ниже\n\n"
            #     f"После оплаты нажми «Я оплатил» ✅",
            #     reply_markup=kb,
            #     parse_mode="HTML"
            # )

            # await message.answer(
            #     "<code>+7 911 313-41-99</code>",
            #     parse_mode="HTML"
            # )

        else:
            await message.answer("❌ Книга не найдена.")
    else:
        await message.answer("👋 Намаскар! Сканируй QR-код в каталоге.")

@dp.callback_query(F.data.startswith("paid_"))
async def paid_handler(callback: CallbackQuery):
    payload = callback.data[len("paid_"):]
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

