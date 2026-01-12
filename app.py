import streamlit as st
import yfinance as yf
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from indicators import MODULLER
from streamlit_plotly_events import plotly_events # Gerekli ek kütüphane

st.set_page_config(page_title="Pro Terminal", layout="wide")

with st.sidebar:
    st.header("📊 Kontrol")
    hisse = st.text_input("Hisse", "AAPL").upper()
    periyot = st.selectbox("Geçmiş", ["1mo", "3mo", "6mo", "1y", "5y"], index=2)
    zaman = st.selectbox("Dilim", ["1d", "1h", "1wk"], index=0)
    tema = st.radio("Tema", ["Siyah", "Beyaz"])
    arkaplan = "#0e1117" if tema == "Siyah" else "white"
    
    st.divider()
    secilenler = st.multiselect("İndikatörler", list(MODULLER.keys()), default=["EMA 7", "RSI"])

try:
    df = yf.download(hisse, period=periyot, interval=zaman)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # --- SABİT BİLGİ ŞERİDİ (GRAFİĞİN ÜSTÜNDE) ---
        # Varsayılan olarak son mumun verilerini gösterir
        last_bar = df.iloc[-1]
        
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Açılış", f"{last_bar['Open']:.2f}")
        c2.metric("Yüksek", f"{last_bar['High']:.2f}")
        c3.metric("Düşük", f"{last_bar['Low']:.2f}")
        c4.metric("Kapanış", f"{last_bar['Close']:.2f}")
        c5.metric("Hacim", f"{int(last_bar['Volume']):,}")

        # --- GRAFİK KURULUMU ---
        osc_list = [i for i in secilenler if MODULLER[i].TYPE == "oscillator"]
        toplam_satir = 1 + len(osc_list)
        satir_oranlari = [0.6] + [0.4/len(osc_list) if osc_list else 0] * len(osc_list)

        fig = make_subplots(rows=toplam_satir, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, row_heights=satir_oranlari)

        x_axis = df.index.strftime("%d/%m %H:%M")

        fig.add_trace(go.Candlestick(
            x=x_axis, open=df['Open'], high=df['High'], 
            low=df['Low'], close=df['Close'], name="Fiyat",
            hoverinfo="x+y" # Mouse ucundaki karmaşayı azalttık
        ), row=1, col=1)

        current_row = 2
        for isim in secilenler:
            modul = MODULLER[isim]
            if modul.TYPE == "overlay":
                fig = modul.ciz(fig, df, x_axis, row=1)
            else:
                fig = modul.ciz(fig, df, x_axis, row=current_row)
                current_row += 1

        # Eksene Bağlama ve Dikey Çizgi
        fig.update_traces(xaxis="x")
        fig.update_xaxes(
            showspikes=True, spikemode="across", spikesnap="cursor",
            spikethickness=1, spikedash="dash", spikecolor="gray",
            showgrid=False, zeroline=False
        )

        fig.update_layout(
            template="plotly_dark" if tema=="Siyah" else "plotly_white",
            paper_bgcolor=arkaplan, plot_bgcolor=arkaplan,
            height=600,
            xaxis_rangeslider_visible=False, xaxis_type='category',
            dragmode='pan', showlegend=False,
            margin=dict(r=50, l=10, t=10, b=10),
            hovermode="x" # Sadece dikey çizgiyi tetikler
        )
        
        fig.update_yaxes(side="right", showgrid=True, gridcolor="rgba(128,128,128,0.1)")

        # Grafiği Çiz
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

except Exception as e:
    st.error(f"Hata oluştu: {e}")
