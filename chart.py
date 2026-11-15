# chart.py
import io
import matplotlib
matplotlib.use("Agg")  # для работы без экрана
import matplotlib.pyplot as plt
import pandas as pd

def draw_chart(df: pd.DataFrame, ticker: str, tf: str, levels: list, fvgs: list) -> io.BytesIO:
    """Рисует график свечей (упрощенно) с уровнями и FVG, возвращает картинку в памяти."""
    # Берем последние 70 свечей для читаемости
    data = df.tail(70).copy()
    
    fig, ax = plt.subplots(figsize=(10, 6), facecolor="#1e1e1e")
    ax.set_facecolor("#1e1e1e")

    # Рисуем свечи
    for i, row in data.iterrows():
        color = "#26a69a" if row["Close"] >= row["Open"] else "#ef5350"
        # Тень свечи
        ax.plot([i, i], [row["Low"], row["High"]], color=color, linewidth=1)
        # Тело свечи
        ax.plot([i, i], [row["Open"], row["Close"]], color=color, linewidth=4)

    # Рисуем уровни (горизонтальные линии)
    for lv in levels:
        color = "#ff9800" if lv["type"] == "resistance" else "#2196f3"
        ax.axhline(y=lv["price"], color=color, linestyle="--", alpha=0.7, linewidth=1.5)
        ax.text(data.index[-1], lv["price"], f" {lv['type']} ({lv['touches']})", 
                color=color, verticalalignment='center')

    # Рисуем имбалансы (FVG) как прямоугольники
    current_price = data["Close"].iloc[-1]
    for fvg in fvgs:
        color = "#4caf50" if fvg["type"] == "bullish" else "#f44336"
        # Рисуем зону только если она близко к текущей цене (в пределах 15%)
        if fvg["distance_pct"] < 15:
            ax.axhspan(fvg["low"], fvg["high"], color=color, alpha=0.2)

    # Настройки осей и внешнего вида
    ax.set_title(f"{ticker} | {tf}", color="white", fontsize=14, pad=15)
    ax.tick_params(colors="white")
    ax.grid(color="#333333", linestyle=":", alpha=0.5)
    
    # Убираем лишние отступы
    ax.set_xlim(data.index[0], data.index[-1])
    plt.tight_layout()

    # Сохраняем в картинку
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, facecolor="#1e1e1e")
    plt.close(fig)
    buf.seek(0)
    
    return buf
