import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta
from plotly.subplots import make_subplots

st.set_page_config(page_title="Pro Analiz", layout="wide")
st.title("📈 Pro Trading Paneli")

# Sol Panel
with st.sidebar:
    st.header("⚙️ Ayarlar")
    hisse = st.text_input("Hisse Kodu (Örn: AAPL)", value="AAPL").upper()
    
    # Zaman Aralığı ve Periyot Uyumu
    zaman_secenekleri = {
        "4 Saatlik": ["1h", "1mo"], # Yahoo'da 4h için 1h çekip birleştirmek gerekir, en stabil 1h'dir.
        "Günlük": ["1d", "1y"],
        "Haftalık": ["1wk", "2y"],
        "Aylık": ["1mo", "5y"]
    }
    secilen_etiket = st.selectbox("Zaman Dilimi", list(zaman_secenekleri.keys()), index=1)
    
    # Seçilen dile göre otomatik ayarlar
    interval = zaman_secenekleri[secilen_etiket][0]
    period = zaman_secenekleri[secilen_etiket][1]
    
    st.divider()
    ema_list = st.multiselect("EMA Seçimi", [7, 14, 30], default=[7, 14, 30])
    show_rsi = st.checkbox("RSI Göster", value=True)

try:
    # VERİ ÇEKME
    df = yf.download(hisse, period=period, interval=interval, group_by='column')
    
    if df is not None and not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # İNDİKATÖR HESAPLAMALARI
        for p in [7, 14, 30]:
            df[f'EMA{p}'] = ta.ema(df['Close'], length=p)
        df['RSI'] = ta.rsi(df['Close'], length=14)

        # GRAFİK YAPISI
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])

        # Mumlar (Gapless için x ekseni string formatında)
        x_axis = df.index.strftime("%d/%m %H:%M")
        
        fig.add_trace(go.Candlestick(
            x=x_axis, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Fiyat", increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
        ), row=1, col=1)

        # EMA Çizgileri
        colors = {7: 'yellow', 14: 'cyan', 30: 'magenta'}
        for p in ema_list:
            fig.add_trace(go.Scatter(x=x_axis, y=df[f'EMA{p}'], 
                                     line=dict(width=1.5, color=colors[p]), name=f"EMA {p}"), row=1, col=1)

        # RSI Paneli
        if show_rsi:
            fig.add_trace(go.Scatter(x=x_axis, y=df['RSI'], 
                                     line=dict(color='#7e57c2', width=2), name="RSI"), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1, opacity=0.5)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1, opacity=0.5)

        # TASARIM VE ZOOM AYARLARI
        fig.update_layout(
            template="plotly_dark",
            height=800,
            xaxis_rangeslider_visible=False,
            xaxis_type='category', # Gapless barlar
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            dragmode='pan' # Varsayılan olarak el aracı (kaydırma) seçili gelir
        )
        
        # Ekrana basarken config ile SCROLL ZOOM'u açıyoruz
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

    else:
        st.warning("Veri bulunamadı. Lütfen kodu (Örn: BTC-USD veya THYAO.IS) kontrol edin.")

except Exception as e:
    st.error(f"Hata: {e}")
