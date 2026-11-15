# data.py
import yfinance as yf
import pandas as pd
from config import TIMEFRAMES

def normalize_ticker(ticker: str) -> str:
    """Приводит тикер к формату yfinance."""
    t = ticker.strip().upper()
    ru_tickers = {"SBER", "GAZP", "LKOH", "ROSN", "YNDX", "TCSG",
                  "NVTK", "MTLR", "PLZL", "GMKN", "ALRS", "MGNT"}
    if t in ru_tickers and not t.endswith(".ME"):
        return t + ".ME"
    return t

def load_data(ticker: str, tf: str = "1d") -> pd.DataFrame | None:
    """Загружает OHLC-данные. Возвращает DataFrame или None."""
    if tf not in TIMEFRAMES:
        return None
    cfg = TIMEFRAMES[tf]
    t = normalize_ticker(ticker)
    try:
        df = yf.download(
            t,
            interval=cfg["interval"],
            period=cfg["period"],
            progress=False,
            auto_adjust=True,
        )
        if df is None or df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[["Open", "High", "Low", "Close"]].dropna()
        return df
    except Exception:
        return None
