import random
import asyncio
import time
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "8382851704:AAH4WxDQua9uY5H7REyXgpHhtqI7s7eog2Y"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

DB_PATH = "casino.db"

# ---------- ИНИЦИАЛИЗАЦИЯ БАЗЫ ----------
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 1000,
                last_bonus INTEGER DEFAULT 0
            )
        """)
        await db.commit()

asyncio.get_event_loop().run_until_complete(init_db())

# ---------- ФУНКЦИИ БАЗЫ ----------
async def get_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT balance, last_bonus FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        if row:
            return row
        else:
            await db.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
            await db.commit()
            return (1000, 0)

async def update_balance(user_id, amount):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
        await db.commit()

async def set_last_bonus(user_id, timestamp):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET last_bonus=? WHERE user_id=?", (timestamp, user_id))
        await db.commit()

# ---------- КНОПКИ МЕНЮ ----------
def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🎰 Слоты", callback_data="slots"),
        InlineKeyboardButton("🎯 Рулетка", callback_data="roulette"),
        InlineKeyboardButton("💰 Баланс", callback_data="balance"),
        InlineKeyboardButton("🎁 Бонус", callback_data="bonus"),
    )
    return kb

# ---------- СТАРТ ----------
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await get_user(message.from_user.id)
    await message.answer("🎰 Добро пожаловать в Казино-бот!\nВыберите действие:", reply_markup=main_menu())

# ---------- ОБРАБОТКА КНОПОК ----------
@dp.callback_query_handler(lambda c: c.data == "balance")
async def show_balance(call: types.CallbackQuery):
    balance, _ = await get_user(call.from_user.id)
    await call.message.edit_text(f"💰 Ваш баланс: {balance} монет", reply_markup=main_menu())
    await call.answer()

@dp.callback_query_handler(lambda c: c.data == "bonus")
async def daily_bonus(call: types.CallbackQuery):
    balance, last_bonus = await get_user(call.from_user.id)
    now = int(time.time())
    if now - last_bonus >= 86400:
        bonus = random.randint(100, 500)
        await update_balance(call.from_user.id, bonus)
        await set_last_bonus(call.from_user.id, now)
        await call.message.edit_text(f"🎁 Вы получили бонус: +{bonus} монет!", reply_markup=main_menu())
    else:
        hours = (86400 - (now - last_bonus)) // 3600
        await call.message.edit_text(f"⌛ Бонус можно взять через {hours} ч.", reply_markup=main_menu())
    await call.answer()

@dp.callback_query_handler(lambda c: c.data == "slots")
async def play_slots(call: types.CallbackQuery):
    bet = 100
    balance, _ = await get_user(call.from_user.id)
    if balance < bet:
        await call.message.edit_text("❌ Недостаточно монет для игры!", reply_markup=main_menu())
        await call.answer()
        return

    await update_balance(call.from_user.id, -bet)
    symbols = ["🍒", "🍋", "🍉", "⭐", "7️⃣"]

    # Анимация вращения
    for _ in range(3):
        spin = [random.choice(symbols) for _ in range(3)]
        await call.message.edit_text(f"🎰 {' | '.join(spin)}", reply_markup=main_menu())
        await asyncio.sleep(0.5)

    # Финальный результат
    result = [random.choice(symbols) for _ in range(3)]
    if len(set(result)) == 1:
        win = bet * 5
        await update_balance(call.from_user.id, win)
        text = f"{' | '.join(result)}\n🎉 Джекпот! +{win} монет"
    elif len(set(result)) == 2:
        win = bet * 2
        await update_balance(call.from_user.id, win)
        text = f"{' | '.join(result)}\n😎 Повезло! +{win} монет"
    else:
        text = f"{' | '.join(result)}\n💀 Увы, вы проиграли {bet} монет"

    await call.message.edit_text(text, reply_markup=main_menu())
    await call.answer()

@dp.callback_query_handler(lambda c: c.data == "roulette")
async def play_roulette(call: types.CallbackQuery):
    bet = 200
    balance, _ = await get_user(call.from_user.id)
    if balance < bet:
        await call.message.edit_text("❌ Недостаточно монет для игры!", reply_markup=main_menu())
        await call.answer()
        return

    await update_balance(call.from_user.id, -bet)
    win_chance = random.randint(1, 10)
    if win_chance <= 4:
        win = bet * 2
        await update_balance(call.from_user.id, win)
        text = f"🎯 Красное! Вы выиграли {win} монет!"
    else:
        text = f"⚫ Чёрное! Вы проиграли {bet} монет."

    await call.message.edit_text(text, reply_markup=main_menu())
    await call.answer()

# ---------- ЗАПУСК ----------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)