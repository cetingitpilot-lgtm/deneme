import plotly.graph_objects as go
import pandas_ta as ta

BILGI = {"ad": "Bollinger", "tip": "overlay"}

def çiz(fig, df, row):
    bb = ta.bbands(df['Close'])
    fig.add_trace(go.Scatter(x=df.index, y=bb['BBU_20_2.0'], name='BB Üst', line=dict(width=1, color='gray')), row=row, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=bb['BBL_20_2.0'], name='BB Alt', line=dict(width=1, color='gray'), fill='tonexty'), row=row, col=1)
