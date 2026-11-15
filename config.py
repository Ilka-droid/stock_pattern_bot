# config.py

# Telegram
BOT_TOKEN = "9216991449:AAHjhFBUTWUEh9V4J1y0_K-rjnNTjT-VlyQ"  # получить у @BotFather

# Доступные таймфреймы yfinance
TIMEFRAMES = {
    "1m":  {"interval": "1m",  "period": "5d"},
    "5m":  {"interval": "5m",  "period": "1mo"},
    "15m": {"interval": "15m", "period": "1mo"},
    "30m": {"interval": "30m", "period": "1mo"},
    "1h":  {"interval": "1h",  "period": "3mo"},
    "1d":  {"interval": "1d",  "period": "6mo"},
    "1wk": {"interval": "1wk", "period": "2y"},
}
DEFAULT_TF = "1d"

# Параметры поиска уровней
LEVEL_TOUCH_TOLERANCE = 0.01   # 1% — насколько близко цена должна подойти к уровню
LEVEL_MIN_TOUCHES = 2          # минимум касаний, чтобы считать уровень значимым
LEVEL_LOOKBACK = 100           # сколько последних свечей анализировать

# Параметры имбалансов (FVG)
FVG_MIN_SIZE_PCT = 0.3         # минимальный размер разрыва в % от цены
