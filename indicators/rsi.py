import plotly.graph_objects as go
import pandas_ta as ta

BILGI = {"ad": "RSI (14)", "tip": "oscillator"}

def çiz(fig, df, row):
    df['RSI'] = ta.rsi(df['Close'], length=14)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#7E57C2')), row=row, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="rgba(255,0,0,0.5)", row=row, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(0,255,0,0.5)", row=row, col=1)
