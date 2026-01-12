import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="Finansal Analiz", layout="wide")
st.title("📈 Profesyonel Teknik Analiz Paneli")

# Yan Menü
with st.sidebar:
    st.header("⚙️ Ayarlar")
    hisse = st.text_input("Hisse Kodu (Örn: AAPL veya THYAO.IS)", value="AAPL")
    periyot = st.selectbox("Zaman Aralığı", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

try:
    # VERİ ÇEKME - En güvenli yöntem
    raw_data = yf.download(hisse, period=periyot, interval="1d")
    
    if not raw_data.empty:
        # Yahoo Finance'in yeni "Multi-index" hatasını düzeltmek için veriyi temizliyoruz
        data = raw_data.copy()
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Grafik Oluşturma
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            increasing_line_color='#26a69a', # TV Yeşili
            decreasing_line_color='#ef5350', # TV Kırmızısı
            name="Fiyat"
        )])

        fig.update_layout(
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=600,
            margin=dict(l=10, r=10, t=30, b=10),
            yaxis_title="Fiyat ($)",
            xaxis_title="Tarih"
        )

        # Grafiği Çiz
        st.plotly_chart(fig, use_container_width=True)

        # Veri Tablosu (Kontrol için)
        with st.expander("Ham Verileri Gör"):
            st.dataframe(data.tail(10))
    else:
        st.error("Veri çekilemedi. Lütfen internet bağlantınızı veya hisse kodunu kontrol edin.")

except Exception as e:
    st.info("Sistem hazırlanıyor, lütfen sayfayı yenileyin veya bir kod girin.")
    # Hatayı tam anlamak için teknik mesajı buraya yazdıralım
    st.write(f"Hata Detayı: {e}")

# Üstteki kodda eksik kalabilecek pandas kütüphanesini import eklemeyi unutmayın
import pandas as pd
