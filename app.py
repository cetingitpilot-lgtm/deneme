import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta
from plotly.subplots import make_subplots

st.set_page_config(page_title="Pro Trader Terminal", layout="wide")

# Sol Panel Ayarları
with st.sidebar:
    st.header("⚙️ Ayarlar")
    hisse = st.text_input("Hisse Kodu", value="AAPL").upper()
    zaman_dilimi = st.selectbox("Zaman Dilimi", ["1d", "1h", "1wk", "1mo"], index=0)
    periyot = st.selectbox("Geçmiş Veri", ["1mo", "3mo", "6mo", "1y", "5y"], index=3)
    
    st.divider()
    ema_list = st.multiselect("EMA Seçimi", [7, 14, 30], default=[7, 14, 30])
    show_rsi = st.checkbox("RSI Göster", value=True)

try:
    df = yf.download(hisse, period=periyot, interval=zaman_dilimi, group_by='column')
    
    if df is not None and not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # HESAPLAMALAR
        for p in [7, 14, 30]:
            df[f'EMA{p}'] = ta.ema(df['Close'], length=p)
        df['RSI'] = ta.rsi(df['Close'], length=14)

        # GRAFİK YAPISI
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])

        x_axis = df.index.strftime("%d/%m %H:%M")
        
        # 1. Mum Grafiği
        fig.add_trace(go.Candlestick(
            x=x_axis, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Fiyat"
        ), row=1, col=1)

        # SON FİYAT ETİKETİ (Beyaz Metin)
        last_price = df['Close'].iloc[-1]
        fig.add_hline(y=last_price, line_dash="dash", line_color="white", line_width=1, row=1, col=1,
                     annotation_text=f"  {last_price:.2f}  ", 
                     annotation_position="right", 
                     annotation_bgcolor="gray",
                     annotation_font_color="white", # Metin Rengi Beyaz
                     annotation_font_size=12)

        # EMA'lar ve Son Değer Etiketleri (Beyaz Metin)
        colors = {7: 'yellow', 14: 'cyan', 30: 'magenta'}
        for p in ema_list:
            ema_val = df[f'EMA{p}'].iloc[-1]
            if not pd.isna(ema_val):
                fig.add_trace(go.Scatter(x=x_axis, y=df[f'EMA{p}'], 
                                         line=dict(width=1.5, color=colors[p]), name=f"EMA {p}"), row=1, col=1)
                
                fig.add_hline(y=ema_val, line_dash="dot", line_color=colors[p], line_width=1, row=1, col=1,
                             annotation_text=f" E{p}: {ema_val:.2f} ", 
                             annotation_position="right", 
                             annotation_bgcolor=colors[p],
                             annotation_font_color="white", # EMA Kutusu içi Beyaz Metin
                             annotation_font_size=11)

        # 2. RSI Paneli ve Son Değer Etiketi (Beyaz Metin)
        if show_rsi:
            last_rsi = df['RSI'].iloc[-1]
            fig.add_trace(go.Scatter(x=x_axis, y=df['RSI'], line=dict(color='#7e57c2', width=2), name="RSI"), row=2, col=1)
            
            if not pd.isna(last_rsi):
                fig.add_hline(y=last_rsi, line_dash="dash", line_color="#7e57c2", row=2, col=1,
                             annotation_text=f" RSI: {last_rsi:.1f} ", 
                             annotation_position="right", 
                             annotation_bgcolor="#7e57c2",
                             annotation_font_color="white") # RSI Kutusu içi Beyaz Metin
            
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1, opacity=0.3)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1, opacity=0.3)

        # TASARIM AYARLARI
        fig.update_layout(
            template="plotly_dark",
            height=850,
            xaxis_rangeslider_visible=False,
            xaxis_type='category',
            showlegend=False,
            dragmode='pan',
            margin=dict(r=100) # Etiketler için sağ boşluğu biraz daha artırdım
        )
        
        fig.update_yaxes(side="right", row=1, col=1, tickfont=dict(color="white"))
        fig.update_yaxes(side="right", row=2, col=1, tickfont=dict(color="white"))

        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

    else:
        st.warning("Veri bulunamadı.")

except Exception as e:
    st.error(f"Hata: {e}")
