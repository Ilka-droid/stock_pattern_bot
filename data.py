# data.py
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from config import TIMEFRAMES

# Настройка интервалов TradingView
TV_INTERVALS = {
    "1m": Interval.in_1_minute,
    "5m": Interval.in_5_minute,
    "15m": Interval.in_15_minute,
    "30m": Interval.in_30_minute,
    "1h": Interval.in_1_hour,
    "1d": Interval.in_daily,
    "1wk": Interval.in_weekly,
}

# Российские тикеры
RU_TICKERS = {"SBER", "GAZP", "LKOH", "ROSN", "YNDX", "TCSG", "NVTK", "MTLR", "PLZL", "GMKN", "ALRS", "MGNT"}

def normalize_ticker(ticker: str) -> str:
    return ticker.strip().upper()

def load_data(ticker: str, tf: str = "1d") -> pd.DataFrame | None:
    if tf not in TIMEFRAMES:
        return None
    
    t = normalize_ticker(ticker)
    interval = TV_INTERVALS[tf]
    
    # Определяем биржу
    if t in RU_TICKERS:
        exchange = "MOEX"
    else:
        exchange = "NASDAQ"  # или NYSE, TradingView сам подтянет
        
    try:
        # Анонимный вход в TradingView
        tv = TvDatafeed()
        # Загружаем данные
        df = tv.get_hist(symbol=t, exchange=exchange, interval=interval, n_bars=500)
        
        if df is None or df.empty:
            return None
            
        # Переименовываем колонки для удобства
        df = df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"})
        return df
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return None
