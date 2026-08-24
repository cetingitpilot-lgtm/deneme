import plotly.graph_objects as go
import pandas_ta as ta

BILGI = {"ad": "Stoch RSI", "tip": "oscillator"}

def çiz(fig, df, row):
    # Hesaplama
    stoch = ta.stochrsi(df['Close'])
    
    # None veya boş dönme kontrolü
    if stoch is None or stoch.empty:
        raise ValueError("Stoch RSI hesaplanamadı, veri yetersiz veya hatalı.")
    
    # pandas_ta stochrsi çıktısı 2 sütundur: [STOCHRSIk, STOCHRSId]
    # Sütun adlarına bağımlı kalmamak için iloc (pozisyon) kullanıyoruz
    stoch_k = stoch.iloc[:, 0]
    stoch_d = stoch.iloc[:, 1]
    
    # Stoch K Çizgisi (Mavi)
    fig.add_trace(
        go.Scatter(
            x=df.index, 
            y=stoch_k, 
            name='Stoch K', 
            line=dict(color='#2962FF', width=1.5)
        ), 
        row=row, col=1
    )
    
    # Stoch D Çizgisi (Turuncu)
    fig.add_trace(
        go.Scatter(
            x=df.index, 
            y=stoch_d, 
            name='Stoch D', 
            line=dict(color='#FF6D00', width=1.5)
        ), 
        row=row, col=1
    )
    
    # Aşırı Alım (80) ve Aşırı Satım (20) Referans Çizgileri
    fig.add_hline(y=80, line_dash="dot", line_color="rgba(255, 255, 255, 0.3)", line_width=1, row=row, col=1)
    fig.add_hline(y=20, line_dash="dot", line_color="rgba(255, 255, 255, 0.3)", line_width=1, row=row, col=1)
