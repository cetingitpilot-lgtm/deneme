import pandas as pd
import plotly.graph_objects as go

NAME = "MACD"
TYPE = "oscillator"

def ciz(fig, df, x_axis, row):
    close = df["Close"]

    # === MACD HESAPLAMA (MANUEL) ===
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()

    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal

    colors = ["green" if v >= 0 else "red" for v in hist]

    fig.add_bar(
        x=x_axis,
        y=hist,
        marker_color=colors,
        name="Histogram",
        row=row,
        col=1
    )

    fig.add_scatter(
        x=x_axis,
        y=macd,
        name="MACD",
        line=dict(color="dodgerblue", width=1.5),
        row=row,
        col=1
    )

    fig.add_scatter(
        x=x_axis,
        y=signal,
        name="Signal",
        line=dict(color="orange", width=1),
        row=row,
        col=1
    )

    # SABİT BAŞLIK
    fig.add_annotation(
        text=NAME,
        xref="paper",
        yref="paper",
        x=0.01,
        y=1 - (row - 1) * 0.18,
        showarrow=False,
        font=dict(size=12, color="white"),
        bgcolor="rgba(0,0,0,0.5)"
    )

    return fig
