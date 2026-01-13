import plotly.graph_objects as go
import pandas_ta as ta

BILGI = {"ad": "MACD (12,26,9)", "tip": "oscillator"}

def çiz(fig, df, row):
    macd = ta.macd(df['Close'])
    df['M'] = macd['MACD_12_26_9']
    df['S'] = macd['MACDs_12_26_9']
    df['H'] = macd['MACDh_12_26_9']
    
    # Sıfırın üstü yeşil, altı kırmızı
    renkler = ['#26a69a' if val >= 0 else '#ef5350' for val in df['H']]
    
    fig.add_trace(go.Scatter(x=df.index, y=df['M'], name='MACD', line=dict(color='#2962FF')), row=row, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['S'], name='Signal', line=dict(color='#FF6D00')), row=row, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['H'], name='Histogram', marker_color=renkler), row=row, col=1)
