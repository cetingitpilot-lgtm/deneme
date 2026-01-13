import pandas as pd
import plotly.graph_objects as go

NAME = "Bollinger"
TYPE = "overlay"

def ciz(fig, df, x_axis, row):
    close = df["Close"]

    period = 20
    std_mult = 2

    middle = close.rolling(period).mean()
    std = close.rolling(period).std()

    upper = middle + std_mult * std
    lower = middle - std_mult * std

    fig.add_scatter(
        x=x_axis,
        y=upper,
        line=dict(color="rgba(0,200,255,0.8)", width=1),
        name="BB Üst",
        row=row,
        col=1
    )

    fig.add_scatter(
        x=x_axis,
        y=lower,
        line=dict(color="rgba(0,200,255,0.8)", width=1),
        fill="tonexty",
        fillcolor="rgba(0,200,255,0.12)",
        name="BB Alt",
        row=row,
        col=1
    )

    fig.add_scatter(
        x=x_axis,
        y=middle,
        line=dict(color="rgba(0,200,255,0.4)", dash="dot"),
        name="BB Orta",
        row=row,
        col=1
    )

    return fig
