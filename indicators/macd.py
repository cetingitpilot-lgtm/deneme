import pandas_ta as ta
import plotly.graph_objects as go

def ciz(fig, df, x, row):
    macd = ta.macd(df["Close"])

    macd_line = macd.iloc[:, 0]
    signal = macd.iloc[:, 1]
    hist = macd.iloc[:, 2]

    colors = ["green" if v >= 0 else "red" for v in hist]

    fig.add_trace(go.Bar(
        x=x,
        y=hist,
        marker_color=colors,
        name="MACD Hist"
    ))

    fig.add_trace(go.Scatter(x=x, y=macd_line, name="MACD", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=x, y=signal, name="Signal", line=dict(color="orange")))

    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.01, y=0.95,
        text="MACD",
        showarrow=False
    )

    return fig
