import pandas_ta as ta
import plotly.graph_objects as go

NAME = "MACD"
TYPE = "oscillator"

def ciz(fig, df, x_axis, row):
    macd = ta.macd(df["Close"])
    hist = macd["MACDh_12_26_9"]

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
        y=macd["MACD_12_26_9"],
        name="MACD",
        line=dict(color="blue"),
        row=row,
        col=1
    )

    fig.add_scatter(
        x=x_axis,
        y=macd["MACDs_12_26_9"],
        name="Signal",
        line=dict(color="orange"),
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
