import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="Finansal Analiz", layout="wide")
st.title("📈 Hisse Senedi Teknik Analiz")

# Yan Menü
hisse_adi = st.sidebar.text_input("Hisse Kodu (Örn: THYAO.IS veya AAPL)", value="THYAO.IS")
periyot = st.sidebar.selectbox("Zaman Aralığı", ["1mo", "3mo", "6mo", "1y", "2y", "5y"])

try:
    # Veriyi indir
    data = yf.download(hisse_adi, period=periyot, interval="1d")
    
    if data.empty:
        st.warning("Veri bulunamadı. Lütfen kodu doğru girdiğinizden emin olun (Örn: THYAO.IS)")
    else:
        # Mum Grafiği
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close']
        )])
        
        fig.update_layout(
            title=f"{hisse_adi} Fiyat Grafiği",
            yaxis_title="Fiyat",
            xaxis_title="Tarih",
            template="plotly_dark", # TradingView gibi koyu tema
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Hareketli Ortalama Ekleme (Basit bir indikatör örneği)
        data['MA20'] = data['Close'].rolling(window=20).mean()
        st.subheader("Son 5 Günlük Veri Özeti")
        st.dataframe(data.tail())

except Exception as e:
    st.error(f"Bir hata oluştu: {e}")
