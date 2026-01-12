import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="Pro Analiz Paneli", layout="wide")

# Sol Panel - Ayarlar
with st.sidebar:
    st.header("📊 Kontrol Paneli")
    hisse = st.text_input("Hisse Kodu", value="AAPL")
    
    # Zaman Aralığı Seçimi (Aralık ve Periyot eşleşmesi)
    interval_dict = {
        "4 Saatlik": "1h", # Yahoo'da 4h kısıtlıdır, 1h en sağlıklısıdır
        "Günlük": "1d",
        "Haftalık": "1wk",
        "Aylık": "1mo"
    }
    secilen_zaman = st.selectbox("Zaman Dilimi", list(interval_dict.keys()), index=1)
    periyot = st.selectbox("Geçmiş Veri", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)
    
    st.divider()
    st.subheader("İndikatörler")
    show_ema7 = st.checkbox("EMA 7", value=True)
    show_ema14 = st.checkbox("EMA 14")
    show_ema30 = st.checkbox("EMA 30")
    show_rsi = st.checkbox("RSI (14)", value=True)

try:
    # Veri Çekme
    interval = interval_dict[secilen_zaman]
    data = yf.download(hisse, period=periyot, interval=interval)

    if not data.empty:
        # Multi-index temizleme
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # HESAPLAMALAR
        # EMA Hesaplamaları
        data['EMA7'] = ta.ema(data['Close'], length=7)
        data['EMA14'] = ta.ema(data['Close'], length=14)
        data['EMA30'] = ta.ema(data['Close'], length=30)
        # RSI Hesaplama
        data['RSI'] = ta.rsi(data['Close'], length=14)

        # GRAFİK OLUŞTURMA (2 Satırlı: Fiyat ve RSI)
        from plotly.subplots import make_subplots
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.05, 
                           row_heights=[0.7, 0.3])

        # 1. Mum Grafiği (Gapless - Boşluksuz olması için 'category' kullanacağız)
        fig.add_trace(go.Candlestick(
            x=data.index.strftime("%Y-%m-%d %H:%M"),
            open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'],
            name="Fiyat", increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
        ), row=1, col=1)

        # EMA Çizgileri ve Sol Üst Lejant Etkisi
        if show_ema7:
            fig.add_trace(go.Scatter(x=data.index.strftime("%Y-%m-%d %H:%M"), y=data['EMA7'], 
                                     line=dict(color='yellow', width=1.5), name='EMA 7'), row=1, col=1)
        if show_ema14:
            fig.add_trace(go.Scatter(x=data.index.strftime("%Y-%m-%d %H:%M"), y=data['EMA14'], 
                                     line=dict(color='cyan', width=1.5), name='EMA 14'), row=1, col=1)
        if show_ema30:
            fig.add_trace(go.Scatter(x=data.index.strftime("%Y-%m-%d %H:%M"), y=data['EMA30'], 
                                     line=dict(color='magenta', width=1.5), name='EMA 30'), row=1, col=1)

        # 2. RSI Grafiği
        if show_rsi:
            fig.add_trace(go.Scatter(x=data.index.strftime("%Y-%m-%d %H:%M"), y=data['RSI'], 
                                     line=dict(color='#7e57c2', width=2), name='RSI'), row=2, col=1)
            # RSI Sınır Çizgileri
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.3, row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.3, row=2, col=1)

        # Tasarım Ayarları
        fig.update_layout(
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=800,
            showlegend=True, # Sol/Sağ üstte hangi çizginin ne olduğunu gösterir
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis_type='category' # GAPLESS (Boşluksuz) görünümü sağlayan kritik ayar
        )
        
        # Hafta sonu boşluklarını gizlemek için kategori bazlı eksen
        fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("Veri bulunamadı.")

except Exception as e:
    st.error(f"Hata: {e}")
