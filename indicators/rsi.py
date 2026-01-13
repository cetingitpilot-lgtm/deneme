import pandas_ta as ta
import plotly.graph_objects as go

def ciz(fig, df, x, row):
    rsi = ta.rsi(df["Close"])

    fig.add_trace(go.Scatter(x=x, y=rsi, name="RSI", line=dict(color="purple")))

    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.01, y=0.90,
        text="RSI",
        showarrow=False
    )

    return fig
