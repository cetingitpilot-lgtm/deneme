import plotly.graph_objects as go
import pandas_ta as ta

BILGI = {"ad": "EMA 14", "tip": "overlay"}

def çiz(fig, df, row):
    df['ema14'] = ta.ema(df['Close'], length=14)
    fig.add_trace(go.Scatter(x=df.index, y=df['ema14'], name='EMA 14'), row=row, col=1)
