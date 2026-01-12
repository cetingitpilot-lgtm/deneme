import streamlit as st
import yfinance as yf
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from indicators import MODULLER # Burası sihirli kısım!

st.set_page_config(page_title="Pro Terminal", layout="wide")

# Sidebar
with st.sidebar:
    st.header("📊 Kontrol")
    hisse = st.text_input("Hisse", "AAPL").upper()
    periyot = st.selectbox("Geçmiş", ["1mo", "3mo", "6mo", "1y", "5y"], index=2)
    zaman = st.selectbox("Dilim", ["1d", "1h", "1wk"], index=0)
    tema = st.radio("Tema", ["Siyah", "Beyaz"])
    
    st.divider()
    # Klasördeki her şeyi otomatik listeler
    secilenler = st.multiselect("İndikatörler", list(MODULLER.keys()), default=["EMA 7", "RSI"])

try:
    df = yf.download(hisse, period=periyot, interval=zaman)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Panel Sayısını Hesapla
        osc_list = [i for i in secilenler if MODULLER[i].TYPE == "oscillator"]
        toplam_satir = 1 + len(osc_list)
        satir_oranlari = [0.6] + [0.4/len(osc_list) if osc_list else 0] * len(osc_list)

        fig = make_subplots(rows=toplam_satir, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, row_heights=satir_oranlari)

        x_axis = df.index.strftime("%d/%m %H:%M")

        # 1. Ana Fiyat (Her zaman 1. satır)
        fig.add_trace(go.Candlestick(x=x_axis, open=df['Open'], high=df['High'], 
                                   low=df['Low'], close=df['Close'], name="Fiyat"), row=1, col=1)

        # 2. İndikatörleri Dinamik Olarak Çiz
        current_row = 2
        for isim in secilenler:
            modul = MODULLER[isim]
            if modul.TYPE == "overlay":
                fig = modul.ciz(fig, df, x_axis, row=1)
            else:
                fig = modul.ciz(fig, df, x_axis, row=current_row)
                current_row += 1

        # Final Dokunuşları
        fig.update_layout(template="plotly_dark" if tema=="Siyah" else "plotly_white",
                          height=400 + (len(osc_list)*200), xaxis_rangeslider_visible=False,
                          xaxis_type='category', dragmode='pan', showlegend=False)
        fig.update_yaxes(side="right")
        fig.update_xaxes(showticklabels=True, row=toplam_satir, col=1)

        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
except Exception as e:
    st.error(f"Hata oluştu: {e}")
