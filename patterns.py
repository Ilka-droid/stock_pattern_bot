# patterns.py
import pandas as pd
from config import LEVEL_TOUCH_TOLERANCE, LEVEL_MIN_TOUCHES, LEVEL_LOOKBACK, FVG_MIN_SIZE_PCT

def find_levels(df: pd.DataFrame) -> list[dict]:
    """
    Ищет уровни сопротивления/поддержки.
    Уровень = цена, которую касались >= N раз и отскакивали.
    """
    data = df.tail(LEVEL_LOOKBACK).copy()
    highs = data["High"].values
    lows = data["Low"].values

    levels = []

    # Ищем локальные максимумы (сопротивление)
    for i in range(1, len(highs) - 1):
        if highs[i] >= highs[i-1] and highs[i] >= highs[i+1]:
            level_price = highs[i]
            touches = 1
            for j in range(len(highs)):
                if j == i:
                    continue
                if abs(highs[j] - level_price) / level_price <= LEVEL_TOUCH_TOLERANCE:
                    touches += 1
            if touches >= LEVEL_MIN_TOUCHES:
                levels.append({
                    "price": round(float(level_price), 4),
                    "touches": touches,
                    "type": "resistance",
                })

    # Ищем локальные минимумы (поддержка)
    for i in range(1, len(lows) - 1):
        if lows[i] <= lows[i-1] and lows[i] <= lows[i+1]:
            level_price = lows[i]
            touches = 1
            for j in range(len(lows)):
                if j == i:
                    continue
                if abs(lows[j] - level_price) / level_price <= LEVEL_TOUCH_TOLERANCE:
                    touches += 1
            if touches >= LEVEL_MIN_TOUCHES:
                levels.append({
                    "price": round(float(level_price), 4),
                    "touches": touches,
                    "type": "support",
                })

    # Убираем дубликаты
    unique = []
    for lv in sorted(levels, key=lambda x: -x["touches"]):
        if all(abs(lv["price"] - u["price"]) / u["price"] > LEVEL_TOUCH_TOLERANCE for u in unique):
            unique.append(lv)
    return unique[:6]

def find_fvg(df: pd.DataFrame) -> list[dict]:
    """
    Ищет незакрытые Fair Value Gap (имбалансы).
    """
    highs = df["High"].values
    lows = df["Low"].values
    closes = df["Close"].values
    current_price = closes[-1]

    fvgs = []
    for i in range(2, len(df)):
        # FVG вверх
        if lows[i] > highs[i-2]:
            gap_low, gap_high = highs[i-2], lows[i]
            gap_size_pct = (gap_high - gap_low) / gap_low * 100
            if gap_size_pct < FVG_MIN_SIZE_PCT:
                continue
            filled = any(lows[j] <= gap_high for j in range(i+1, len(df)))
            if not filled:
                fvgs.append({
                    "type": "bullish",
                    "low": round(float(gap_low), 4),
                    "high": round(float(gap_high), 4),
                    "size_pct": round(gap_size_pct, 2),
                    "distance_pct": round(abs(current_price - gap_high) / current_price * 100, 2),
                })

        # FVG вниз
        if highs[i] < lows[i-2]:
            gap_low, gap_high = highs[i], lows[i-2]
            gap_size_pct = (gap_high - gap_low) / gap_high * 100
            if gap_size_pct < FVG_MIN_SIZE_PCT:
                continue
            filled = any(highs[j] >= gap_low for j in range(i+1, len(df)))
            if not filled:
                fvgs.append({
                    "type": "bearish",
                    "low": round(float(gap_low), 4),
                    "high": round(float(gap_high), 4),
                    "size_pct": round(gap_size_pct, 2),
                    "distance_pct": round(abs(current_price - gap_low) / current_price * 100, 2),
                })

    return fvgs
