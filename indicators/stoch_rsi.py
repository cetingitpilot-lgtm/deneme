import pandas_ta as ta
import plotly.graph_objects as go

NAME = "Stoch RSI"
TYPE = "oscillator"

def ciz(fig, df, x_axis, row):
    stoch = ta.stochrsi(df["Close"])

    fig.add_scatter(
        x=x_axis,
        y=stoch["STOCHRSIk_14_14_3_3"],
        name="%K",
        row=row,
        col=1
    )

    fig.add_scatter(
        x=x_axis,
        y=stoch["STOCHRSId_14_14_3_3"],
        name="%D",
        row=row,
        col=1
    )

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
