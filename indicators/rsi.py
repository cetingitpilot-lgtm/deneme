import pandas_ta as ta
import plotly.graph_objects as go

NAME = "RSI"
TYPE = "oscillator"

def ciz(fig, df, x_axis, row):
    rsi = ta.rsi(df["Close"])

    fig.add_scatter(
        x=x_axis,
        y=rsi,
        name="RSI",
        line=dict(color="purple"),
        row=row,
        col=1
    )

    fig.add_hline(y=70, line_dash="dot", row=row, col=1)
    fig.add_hline(y=30, line_dash="dot", row=row, col=1)

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
