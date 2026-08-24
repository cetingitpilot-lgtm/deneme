import plotly.graph_objects as go
import pandas_ta as ta

BILGI = {"ad": "MACD (12,26,9)", "tip": "oscillator"}

def çiz(fig, df, row):
    # Hesaplama (Parametreleri açıkça belirtmek iyi bir pratiktir)
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    
    # None veya boş dönme kontrolü
    if macd is None or macd.empty:
        raise ValueError("MACD hesaplanamadı, veri yetersiz veya hatalı.")
    
    # pandas_ta macd çıktısı 3 sütundur: [MACD, Histogram, Signal]
    # Sütun adlarına bağımlı kalmamak için iloc kullanıyoruz
    macd_line = macd.iloc[:, 0]    # MACD çizgisi
    histogram = macd.iloc[:, 1]    # Histogram
    signal_line = macd.iloc[:, 2]  # Sinyal çizgisi
    
    # Sıfırın üstü yeşil, altı kırmızı (Mantığınızı aynen korudum)
    renkler = ['#26a69a' if val >= 0 else '#ef5350' for val in histogram]
    
    # Histogram Çizimi (Barların arkada kalması için ilk çizdirilir)
    fig.add_trace(
        go.Bar(
            x=df.index, 
            y=histogram, 
            name='Histogram', 
            marker_color=renkler
        ), 
        row=row, col=1
    )
    
    # MACD Çizgisi (Mavi)
    fig.add_trace(
        go.Scatter(
            x=df.index, 
            y=macd_line, 
            name='MACD', 
            line=dict(color='#2962FF', width=1.5)
        ), 
        row=row, col=1
    )
    
    # Signal Çizgisi (Turuncu)
    fig.add_trace(
        go.Scatter(
            x=df.index, 
            y=signal_line, 
            name='Signal', 
            line=dict(color='#FF6D00', width=1.5)
        ), 
        row=row, col=1
    )
