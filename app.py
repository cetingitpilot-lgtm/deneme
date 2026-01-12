import streamlit as st
import yfinance as download_data
import plotly.graph_objects as go
import yfinance as yf

# Sayfa Başlığı
st.set_page_config(page_title="Finansal Analiz Paneli")
st.title("📈 Hisse Senedi Görselleştirici")

# Kullanıcıdan Giriş Alma
hisse_adi = st.sidebar.text_input("Hisse Kodu Girin (Örn: AAPL veya THYAO.IS)", value="AAPL")
periyot = st.sidebar.selectbox("Zaman Aralığı", ["1y", "6mo", "1mo", "5y"])

# Veri Çekme
@st.cache_data
def veri_indir(sembol, p):
    df = yf.download(sembol, period=p)
    return df

try:
    data = veri_indir(hisse_adi, periyot)

    # Mum Grafiği (Candlestick) Oluşturma
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Mum Grafiği"
    )])

    fig.update_layout(title=f"{hisse_adi} Grafik", yasxis_title="Fiyat", xaxis_rangeslider_visible=True)

    # Ekrana Çizdirme
    st.plotly_chart(fig, use_container_width=True)

    # Basit Veri Tablosu
    st.subheader("Son Veriler")
    st.write(data.tail())

except:
    st.error("Hisse kodu bulunamadı veya bir hata oluştu. Lütfen doğru formatta girin.")