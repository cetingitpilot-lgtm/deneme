import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# Sayfa Genişliği Ayarı
st.set_page_config(page_title="Finansal Analiz", layout="wide")

st.title("📈 Hisse Senedi Analiz Paneli")

# Yan Menü Ayarları
with st.sidebar:
    st.header("⚙️ Ayarlar")
    hisse = st.text_input("Hisse Kodu (Örn: THYAO.IS veya AAPL)", value="AAPL")
    zaman_araligi = st.selectbox("Zaman Aralığı", ["1mo", "3mo", "6mo", "1y", "5y"], index=3)
    
# Veri Çekme İşlemi
def verileri_getir(ticker, period):
    # Veriyi indiriyoruz (Otomatik düzeltme açık)
    df = yf.download(ticker, period=period, interval="1d", auto_adjust=True)
    return df

try:
    data = verileri_getir(hisse, zaman_araligi)
    
    # Veri gerçekten geldi mi kontrol et
    if data is not None and not data.empty:
        
        # Grafik Hazırlama
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            increasing_line_color= '#26a69a', # TradingView Yeşili
            decreasing_line_color= '#ef5350'  # TradingView Kırmızısı
        )])

        fig.update_layout(
            title=f"{hisse} Teknik Analiz Grafiği",
            template="plotly_dark", # Karanlık tema
            xaxis_rangeslider_visible=False, # Alttaki küçük kaydırıcıyı kapat (TV stili)
            height=700,
            yaxis_title="Fiyat (Para Birimi)"
        )

        # Grafiği Ekrana Bas
        st.plotly_chart(fig, use_container_width=True)
        
        # Alt kısma küçük bir özet tablo
        st.subheader("📊 Son Fiyat Hareketleri")
        st.dataframe(data.tail(10), use_container_width=True)

    else:
        st.error(f"'{hisse}' kodlu veri alınamadı. Lütfen kodu kontrol edin.")
        st.info("İpucu: Türkiye borsası için sonuna .IS ekleyin (Örn: EREGL.IS). ABD hisseleri için sadece kod (Örn: TSLA).")

except Exception as e:
    st.error(f"Beklenmedik bir hata: {e}")
