import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta

st.set_page_config(page_title="Pro Analiz", layout="wide")

# Sol Panel
with st.sidebar:
    st.header("⚙️ Ayarlar")
    hisse = st.text_input("Hisse Kodu (Örn: AAPL)", value="AAPL").upper()
    zaman_dilimi = st.selectbox("Zaman Dilimi", ["1d", "1h", "1wk", "1mo"], index=0)
    periyot = st.selectbox("Geçmiş Veri", ["1mo", "3mo", "6mo", "1y", "5y"], index=3)
    
    st.divider()
    ema_list = st.multiselect("EMA Seçimi", [7, 14, 30], default=[7])
    show_rsi = st.checkbox("RSI Göster", value=True)

try:
    # Veriyi çek ve Multi-index hatasını temizle
    df = yf.download(hisse, period=periyot, interval=zaman_dilimi, group_by='column')
    
    if df is not None and not df.empty:
        # Veriyi düzleştir (Çok katmanlı sütunları tek katmana indir)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # İndikatör Hesaplamaları
        if 7 in ema_list: df['EMA7'] = ta.ema(df['Close'], length=7)
        if 14 in ema_list: df['EMA14'] = ta.ema(df['Close'], length=14)
        if 30 in ema_list: df['EMA30'] = ta.ema(df['Close'], length=30)
        df['RSI'] = ta.rsi(df['Close'], length=14)

        # Grafik Panelleri (Fiyat ve RSI)
        from plotly.subplots import make_subplots
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])

        # Mum Grafiği (Gapless - Kategorik Eksen)
        fig.add_trace(go.Candlestick(
            x=df.index.strftime("%d-%m %H:%M"),
            open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Fiyat"
        ), row=1, col=1)

        # EMA'lar ve Dinamik İsimlendirme
        colors = {7: 'yellow', 14: 'cyan', 30: 'magenta'}
        for period in ema_list:
            fig.add_trace(go.Scatter(x=df.index.strftime("%d-%m %H:%M"), y=df[f'EMA{period}'], 
                                     line=dict(width=1.5, color=colors[period]), name=f"EMA {period}"), row=1, col=1)

        # RSI Paneli
        if show_rsi:
            fig.add_trace(go.Scatter(x=df.index.strftime("%d-%m %H:%M"), y=df['RSI'], 
                                     line=dict(color='#7e57c2'), name="RSI"), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        # Görsel Ayarlar
        fig.update_layout(template="plotly_dark", height=750, showlegend=True,
                          xaxis_rangeslider_visible=False, xaxis_type='category',
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"{hisse} için veri çekilemedi. Lütfen kodu doğru girdiğinizden emin olun.")

except Exception as e:
    st.error(f"Teknik bir sorun oluştu: {e}")
