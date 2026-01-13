import plotly.graph_objects as go
import pandas_ta as ta

BILGI = {"ad": "EMA 30", "tip": "overlay"}

def çiz(fig, df, row):
    df['ema30'] = ta.ema(df['Close'], length=30)
    fig.add_trace(go.Scatter(x=df.index, y=df['ema30'], name='EMA 30'), row=row, col=1)
