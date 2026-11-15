# chart.py
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

def draw_chart(df: pd.DataFrame, ticker: str, tf: str, levels: list, fvgs: list) -> io.BytesIO:
    data = df.tail(70).copy()
    
    # Делаем 2 графика: сверху цена, снизу объемы
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), facecolor="#1e1e1e", gridspec_kw={'height_ratios': [3, 1]})
    ax1.set_facecolor("#1e1e1e")
    ax2.set_facecolor("#1e1e1e")

    # Рисуем свечи на ax1
    for i, row in data.iterrows():
        color = "#26a69a" if row["Close"] >= row["Open"] else "#ef5350"
        ax1.plot([i, i], [row["Low"], row["High"]], color=color, linewidth=1)
        ax1.plot([i, i], [row["Open"], row["Close"]], color=color, linewidth=4)

    # Уровни
    for lv in levels:
        color = "#ff9800" if lv["type"] == "resistance" else "#2196f3"
        ax1.axhline(y=lv["price"], color=color, linestyle="--", alpha=0.7, linewidth=1.5)

    # FVG
    for fvg in fvgs:
        color = "#4caf50" if fvg["type"] == "bullish" else "#f44336"
        if fvg["distance_pct"] < 15:
            ax1.axhspan(fvg["low"], fvg["high"], color=color, alpha=0.2)

    ax1.set_title(f"{ticker} | {tf}", color="white", fontsize=14, pad=15)
    ax1.tick_params(colors="white")
    ax1.grid(color="#333333", linestyle=":", alpha=0.5)
    ax1.set_xlim(data.index[0], data.index[-1])

    # Рисуем объемы на ax2
    for i, row in data.iterrows():
        color = "#26a69a" if row["Close"] >= row["Open"] else "#ef5350"
        ax2.bar(i, row["Volume"], color=color, alpha=0.7, width=0.6)
    
    ax2.tick_params(colors="white")
    ax2.grid(color="#333333", linestyle=":", alpha=0.5)
    ax2.set_xlim(data.index[0], data.index[-1])
    ax2.set_ylabel("Volume", color="white")

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, facecolor="#1e1e1e")
    plt.close(fig)
    buf.seek(0)
    return buf
