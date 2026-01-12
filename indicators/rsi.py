import pandas_ta as ta
import plotly.graph_objects as go
import numpy as np

NAME = "RSI"
TYPE = "oscillator"

def ciz(fig, df, x_axis, row):
    # 1. RSI ve Ortalama Hesaplama
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['RSI_MA'] = ta.sma(df['RSI'], length=14)

    # 2. Referans Çizgileri (70 ve 30)
    # add_hline yerine Scatter kullanarak her zaman görünmesini sağlıyoruz
    line_x = [x_axis[0], x_axis[-1]] # Başlangıç ve bitiş noktaları
    
    # 70 Çizgisi
    fig.add_trace(go.Scatter(
        x=line_x, y=[70, 70],
        mode="lines",
        line=dict(color="red", width=1.5, dash="dash"),
        name="Aşırı Alım (70)",
        showlegend=False,
        hoverinfo='skip'
    ), row=row, col=1)

    # 30 Çizgisi
    fig.add_trace(go.Scatter(
        x=line_x, y=[30, 30],
        mode="lines",
        line=dict(color="green", width=1.5, dash="dash"),
        name="Aşırı Satım (30)",
        showlegend=False,
        hoverinfo='skip'
    ), row=row, col=1)

    # 3. RSI 14-Bar Hareketli Ortalama (Sarı)
    fig.add_trace(go.Scatter(
        x=x_axis, y=df['RSI_MA'], 
        name="RSI SMA 14", 
        line=dict(color='#FFD700', width=1.5)
    ), row=row, col=1)

    # 4. Ana RSI Çizgisi (Mor)
    fig.add_trace(go.Scatter(
        x=x_axis, y=df['RSI'], 
        name="RSI", 
        line=dict(color='#7e57c2', width=2)
    ), row=row, col=1)

    # 5. Y Eksenini Sınırla
    fig.update_yaxes(range=[0, 100], row=row, col=1)

    return fig
