import pandas_ta as ta
import plotly.graph_objects as go

NAME = "Stoch RSI"
TYPE = "oscillator"

def ciz(fig, df, x_axis, row):
    s = ta.stochrsi(df['Close'])
    fig.add_trace(go.Scatter(x=x_axis, y=s['STOCHRSIk_14_14_3_3'], name="Stoch K", line=dict(color="white")), row=row, col=1)
    fig.add_trace(go.Scatter(x=x_axis, y=s['STOCHRSId_14_14_3_3'], name="Stoch D", line=dict(color="orange")), row=row, col=1)
    return fig
