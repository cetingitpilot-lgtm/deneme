import pandas_ta as ta
import plotly.graph_objects as go

NAME = "RSI"
TYPE = "oscillator"

def ciz(fig, df, x_axis, row):
    # 1. RSI ve RSI Ortalamasını (14 bar) Hesapla
    df['RSI'] = ta.rsi(df['Close'], length=14)
    # RSI'ın kendi üzerinden 14 barlık SMA (Basit Hareketli Ortalama) alıyoruz
    df['RSI_MA'] = ta.sma(df['RSI'], length=14)

    # 2. Ana RSI Çizgisi (Mor)
    fig.add_trace(go.Scatter(
        x=x_axis, y=df['RSI'], 
        name="RSI", 
        line=dict(color='#7e57c2', width=2)
    ), row=row, col=1)

    # 3. RSI 14-Bar Hareketli Ortalama (Sarı)
    fig.add_trace(go.Scatter(
        x=x_axis, y=df['RSI_MA'], 
        name="RSI SMA 14", 
        line=dict(color='#FFD700', width=1.5)
    ), row=row, col=1)

    # 4. Referans Çizgileri (70 Kırmızı, 30 Yeşil)
    # 70 Seviyesi (Aşırı Alım)
    fig.add_hline(y=70, line_dash="dash", line_color="red", 
                  row=row, col=1, opacity=0.5, line_width=1.5)
    
    # 30 Seviyesi (Aşırı Satım)
    fig.add_hline(y=30, line_dash="dash", line_color="green", 
                  row=row, col=1, opacity=0.5, line_width=1.5)

    # 5. Görsel İyileştirme (RSI alanı için Y ekseni sınırlarını sabitleme)
    fig.update_yaxes(range=[0, 100], row=row, col=1)

    return fig
