import plotly.graph_objects as go
import pandas_ta as ta

BILGI = {"ad": "EMA 7", "tip": "overlay"}

def çiz(fig, df, row):
    df['ema7'] = ta.ema(df['Close'], length=7)
    fig.add_trace(go.Scatter(x=df.index, y=df['ema7'], name='EMA 7'), row=row, col=1)
