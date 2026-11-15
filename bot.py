# bot.py
import asyncio
import logging
import os
import gc
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

from config import BOT_TOKEN, DEFAULT_TF, TIMEFRAMES
from data import load_data
from patterns import find_levels, find_fvg
from chart import draw_chart

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я анализирую графики акций.\n\n"
        "Отправь команду:\n"
        "`/check AAPL` — проверить акцию (по умолчанию Д1)\n"
        "`/check SBER 1h` — проверить с таймфреймом\n\n"
        f"Доступные таймфреймы: {', '.join(TIMEFRAMES.keys())}",
        parse_mode="Markdown"
    )

@dp.message(Command("check"))
async def cmd_check(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Укажи тикер. Например: `/check AAPL` или `/check SBER 1h`", parse_mode="Markdown")
        return

    ticker = args[1].upper()
    tf = args[2].lower() if len(args) > 2 else DEFAULT_TF

    if tf not in TIMEFRAMES:
        await message.answer(f"❌ Неизвестный таймфрейм. Доступные: {', '.join(TIMEFRAMES.keys())}")
        return

    msg = await message.answer(f"⏳ Анализирую {ticker} ({tf})...")

    df = await asyncio.to_thread(load_data, ticker, tf)
    
    if df is None or df.empty:
        await msg.edit_text(f"❌ Не удалось загрузить данные по тикеру {ticker}. Проверь правильность написания.")
        return

    levels = find_levels(df)
    fvgs = find_fvg(df)

    report = f"📊 **{ticker}** ({tf})\n\n"
    
    # Анализ объема
    if "Volume" in df.columns and len(df) > 0:
        avg_volume = df["Volume"].tail(20).mean()
        last_volume = df["Volume"].iloc[-1]
        if last_volume > avg_volume * 1.5:
            report += "📊 **Объем:** ВЫСОКИЙ (сильные игроки)\n\n"
        else:
            report += "📊 **Объем:** Средний/Низкий\n\n"
    
    if levels:
        report += "📍 **Найденные уровни:**\n"
        for lv in levels:
            type_ru = "Сопротивление" if lv['type'] == 'resistance' else "Поддержка"
            report += f"• {type_ru}: {lv['price']} (касаний: {lv['touches']})\n"
    else:
        report += "📍 Уровни не найдены.\n"

    report += "\n"
    
    if fvgs:
        report += "⚡ **Имбалансы (FVG):**\n"
        for fvg in fvgs[:3]:
            type_ru = "Бычий" if fvg['type'] == 'bullish' else "Медвежий"
            report += f"• {type_ru}: {fvg['low']} - {fvg['high']} (до цены: {fvg['distance_pct']}%)\n"
    else:
        report += "⚡ Имбалансы не найдены.\n"

    await msg.edit_text(report, parse_mode="Markdown")

    # --- Рисуем график и отправляем ---
    try:
        chart_buf = await asyncio.to_thread(draw_chart, df, ticker, tf, levels, fvgs)
        photo = BufferedInputFile(chart_buf.read(), filename=f"{ticker}_{tf}.png")
        await message.answer_photo(photo, caption=f"График {ticker} ({tf})")
        gc.collect() # Очищаем память после отправки, чтобы сервер не зависал
    except Exception as e:
        await message.answer(f"⚠️ Не удалось нарисовать график: {e}")

# --- Мини-сервер для бесплатного хостинга ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_fake_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    threading.Thread(target=run_fake_server, daemon=True).start()
    asyncio.run(main())
