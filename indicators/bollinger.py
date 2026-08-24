import plotly.graph_objects as go
import pandas_ta as ta

BILGI = {"ad": "Bollinger", "tip": "overlay"}

def çiz(fig, df, row):
    # Hesaplama
    bb = ta.bbands(df['Close'], length=20, std=2)
    
    # None veya boş dönme kontrolü
    if bb is None or bb.empty:
        raise ValueError("Bollinger Bantları hesaplanamadı, veri yetersiz veya hatalı.")
    
    # Sütun adlarına bağımlı kalmamak için iloc (pozisyonel indeks) kullanın
    # pandas_ta bbands çıktısı sırasıyla: [BBL (Alt), BBM (Orta), BBU (Üst), BBB, BBP]
    bbl = bb.iloc[:, 0]  # BB Alt
    bbu = bb.iloc[:, 2]  # BB Üst

    # Üst Bant Çizimi
    fig.add_trace(
        go.Scatter(
            x=df.index, 
            y=bbu, 
            name='BB Üst', 
            line=dict(width=1, color='gray')
        ), 
        row=row, col=1
    )
    
    # Alt Bant Çizimi (Üst banda kadar olan alanı doldurur)
    fig.add_trace(
        go.Scatter(
            x=df.index, 
            y=bbl, 
            name='BB Alt', 
            line=dict(width=1, color='gray'), 
            fill='tonexty'
        ), 
        row=row, col=1
    )
