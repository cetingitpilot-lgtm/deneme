import plotly.graph_objects as go
import pandas_ta as ta

BILGI = {"ad": "Stoch RSI", "tip": "oscillator"}

def çiz(fig, df, row):
    stoch = ta.stochrsi(df['Close'])
    fig.add_trace(go.Scatter(x=df.index, y=stoch['STOCHRSIk_14_14_3_3'], name='Stoch K'), row=row, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=stoch['STOCHRSId_14_14_3_3'], name='Stoch D'), row=row, col=1)
