import pandas_ta as ta
import plotly.graph_objects as go

NAME = "MACD"
TYPE = "oscillator"

def ciz(fig, df, x_axis, row):
    m = ta.macd(df['Close'])
    fig.add_trace(go.Scatter(x=x_axis, y=m['MACD_12_26_9'], name="MACD", line=dict(color="#2196f3")), row=row, col=1)
    fig.add_trace(go.Scatter(x=x_axis, y=m['MACDs_12_26_9'], name="Signal", line=dict(color="#ff9800")), row=row, col=1)
    # Histogram
    fig.add_trace(go.Bar(x=x_axis, y=m['MACDh_12_26_9'], name="Hist", opacity=0.5), row=row, col=1)
    return fig
