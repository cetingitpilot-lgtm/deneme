import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta
from plotly.subplots import make_subplots

# Sayfa Yapılandırması
st.set_page_config(page_title="Pro Trader Terminal", layout="wide")

# --- SOL PANEL (AYARLAR) ---
with st.sidebar:
    st.header("⚙️ Ayarlar")
    hisse = st.text_input("Hisse Kodu", value="AAPL").upper()
    zaman_dilimi = st.selectbox("Zaman Dilimi", ["1d", "1h", "1wk", "1mo"], index=0)
    periyot = st.selectbox("Geçmiş Veri", ["1mo", "3mo", "6mo", "1y", "5y"], index=3)
    
    st.divider()
    # TEMA SEÇİMİ
    tema = st.radio("Grafik Teması", ["Siyah", "Beyaz"], index=0)
    tema_kodu = "plotly_dark" if tema == "Siyah" else "plotly_white"
    metin_rengi = "white" if tema == "Siyah" else "black"
    arkaplan_rengi = "#0e1117" if tema == "Siyah" else "white"
    
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
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        x_axis = df.index.strftime("%d/%m %H:%M")
        
        # 1. Mum Grafiği
        fig.add_trace(go.Candlestick(
            x=x_axis, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Fiyat"
        ), row=1, col=1)

        # --- ETİKETLER VE ÇİZGİLER ---
        # Son Fiyat
        last_price = df['Close'].iloc[-1]
        fig.add_hline(y=last_price, line_dash="dash", line_color="gray", line_width=1, row=1, col=1)

        # EMA'lar
        colors = {7: 'yellow', 14: 'cyan', 30: 'magenta'}
        for p in ema_list:
            ema_val = df[f'EMA{p}'].iloc[-1]
            if not pd.isna(ema_val):
                fig.add_trace(go.Scatter(x=x_axis, y=df[f'EMA{p}'], 
                                         line=dict(width=1.5, color=colors[p]), name=f"EMA {p}"), row=1, col=1)

        # RSI Paneli
        if show_rsi:
            fig.add_trace(go.Scatter(x=x_axis, y=df['RSI'], line=dict(color='#7e57c2', width=2), name="RSI"), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1, opacity=0.3)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1, opacity=0.3)

        # --- EKSEN VE GÖRÜNÜM AYARLARI ---
        fig.update_layout(
            template=tema_kodu,
            paper_bgcolor=arkaplan_rengi,
            plot_bgcolor=arkaplan_rengi,
            height=850,
            xaxis_rangeslider_visible=False,
            xaxis_type='category',
            showlegend=True,
            dragmode='pan',
            margin=dict(r=120, l=10, t=50, b=10), # Sağ tarafta geniş alan
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
        )
        
        # Eksen Değerlerinin Görünmesini Sağlayan Ayar
        fig.update_yaxes(
            side="right", 
            row=1, col=1, 
            showgrid=True, 
            gridcolor='rgba(128,128,128,0.2)',
            tickformat=".2f", # Fiyatları 2 basamaklı göster
            nticks=20 # Daha fazla fiyat seviyesi göster
        )
        fig.update_yaxes(side="right", row=2, col=1, showgrid=True, gridcolor='rgba(128,128,128,0.2)')

        # Son Değer Etiketlerini (Sağ taraftaki kutucuklar) Yeniden Tanımlama
        # Bu yöntem eksen değerlerini gizlemez
        # Son Fiyat Etiketi
        fig.add_annotation(xref="paper", yref="y", x=1.02, y=last_price, text=f" {last_price:.2f} ",
                          showarrow=False, bgcolor="gray", font=dict(color="white"), row=1, col=1)
        
        # EMA Etiketleri
        for p in ema_list:
            val = df[f'EMA{p}'].iloc[-1]
            if not pd.isna(val):
                fig.add_annotation(xref="paper", yref="y", x=1.12 if p==14 else (1.22 if p==30 else 1.02), 
                                  y=val, text=f"E{p}:{val:.2f}",
                                  showarrow=False, bgcolor=colors[p], font=dict(color="white"), row=1, col=1)

        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

    else:
        st.warning("Veri bulunamadı.")

except Exception as e:
    st.error(f"Hata: {e}")
