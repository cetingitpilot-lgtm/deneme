import pandas_ta as ta
import plotly.graph_objects as go

def ciz(fig, df, x, row):
    srsi = ta.stochrsi(df["Close"])

    fig.add_trace(go.Scatter(x=x, y=srsi.iloc[:, 0], name="StochRSI K"))
    fig.add_trace(go.Scatter(x=x, y=srsi.iloc[:, 1], name="StochRSI D"))

    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.01, y=0.85,
        text="Stoch RSI",
        showarrow=False
    )

    return fig
