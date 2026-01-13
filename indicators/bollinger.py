import pandas_ta as ta
import plotly.graph_objects as go

NAME = "Bollinger"
TYPE = "overlay"

def ciz(fig, df, x_axis, row):
    bb = ta.bbands(df["Close"], length=20, std=2)

    # HER SÜRÜM İÇİN GÜVENLİ OKUMA
    lower = bb.iloc[:, 0]
    middle = bb.iloc[:, 1]
    upper = bb.iloc[:, 2]

    fig.add_scatter(
        x=x_axis,
        y=upper,
        line=dict(color="rgba(0,200,255,0.7)", width=1),
        name="BB Üst",
        row=row,
        col=1
    )

    fig.add_scatter(
        x=x_axis,
        y=lower,
        line=dict(color="rgba(0,200,255,0.7)", width=1),
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
