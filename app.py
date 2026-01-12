import streamlit as st
import yfinance as yf
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from indicators import MODULLER

st.set_page_config(page_title="Pro Terminal", layout="wide")

# --- CSS (Hover Box Sabitleme) ---
st.markdown("""
    <style>
    [data-testid="stPlotlyChart"] .js-plotly-plot .plotly .hoverlayer {
        transform: translate(10px, 0px) !important;
        position: absolute !important;
        top: 0px !important;
        left: 0px !important;
        z-index: 10000 !important;
        pointer-events: none !important;
    }
    [data-testid="stPlotlyChart"] .js-plotly-plot .plotly .hoverlayer .hovertext text {
        font-family: 'Monospace', monospace !important;
        font-size: 12px !important;
        font-weight: bold !important;
        fill: #ffffff !important;
        text-shadow: 1px 1px 2px black !important;
    }
    [data-testid="stPlotlyChart"] .js-plotly-plot .plotly .hoverlayer .hovertext path {
        fill: rgba(0,0,0,0) !important;
        stroke: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.header("📊 Kontrol")
    hisse = st.text_input("Hisse", "AAPL").upper()
    periyot = st.selectbox("Geçmiş", ["1mo", "3mo", "6mo", "1y", "5y"], index=2)
    zaman = st.selectbox("Dilim", ["1d", "1h", "1wk"], index=0)
    tema = st.radio("Tema", ["Siyah", "Beyaz"])
    arkaplan = "#0e1117" if tema == "Siyah" else "white"
    text_color = "white" if tema == "Siyah" else "black"
    
    st.divider()
    secilenler = st.multiselect("İndikatörler", list(MODULLER.keys()), default=["EMA 7", "RSI"])

try:
    df = yf.download(hisse, period=periyot, interval=zaman)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        osc_list = [i for i in secilenler if MODULLER[i].TYPE == "oscillator"]
        toplam_satir = 1 + len(osc_list)
        satir_oranlari = [0.6] + [0.4/len(osc_list) if osc_list else 0] * len(osc_list)

        # vertical_spacing artırıldı (0.03 -> 0.10) tarihlerin sığması için boşluk açar
        fig = make_subplots(rows=toplam_satir, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.10, row_heights=satir_oranlari)

        x_axis = df.index.strftime("%d/%m %H:%M")

        # 1. Ana Fiyat Grafiği
        fig.add_trace(go.Candlestick(
            x=x_axis, open=df['Open'], high=df['High'], 
            low=df['Low'], close=df['Close'], name="OHLC"
        ), row=1, col=1)

        # 2. İndikatörleri Çiz
        current_row = 2
        for isim in secilenler:
            modul = MODULLER[isim]
            if modul.TYPE == "overlay":
                fig = modul.ciz(fig, df, x_axis, row=1)
            else:
                fig = modul.ciz(fig, df, x_axis, row=current_row)
                current_row += 1

        # 3. Eksen Ayarları ve Tarihlerin Konumu
        fig.update_xaxes(
            showspikes=True, spikemode="across", spikesnap="cursor",
            spikethickness=1, spikedash="dash", spikecolor="gray",
            showgrid=False, zeroline=False,
            xaxis_type='category'
        )

        # ÖNEMLİ: Sadece 1. satırın (Ana Grafik) tarihlerini göster
        for i in range(1, toplam_satir + 1):
            if i == 1:
                fig.update_xaxes(
                    showticklabels=True, 
                    tickangle=-45, 
                    tickfont=dict(size=10),
                    row=1, col=1
                )
            else:
                # Alttaki indikatörlerin tarih etiketlerini kapat
                fig.update_xaxes(showticklabels=False, row=i, col=1)

        # LAYOUT AYARLARI
        fig.update_layout(
            template="plotly_dark" if tema=="Siyah" else "plotly_white",
            paper_bgcolor=arkaplan, plot_bgcolor=arkaplan,
            height=700,
            xaxis_rangeslider_visible=False,
            dragmode='pan', showlegend=False,
            margin=dict(r=50, l=10, t=10, b=10),
            hovermode="x unified",
            hoverdistance=-1,
            hoverlabel=dict(
                bgcolor="rgba(0,0,0,0)",
                bordercolor="rgba(0,0,0,0)",
                namelength=-1,
                font=dict(family="Monospace"),
                align="left"
            )
        )
        
        fig.update_yaxes(side="right", showgrid=True, gridcolor="rgba(128,128,128,0.1)")

        st.plotly_chart(fig, width="stretch", config={'scrollZoom': True})

except Exception as e:
    st.error(f"Hata oluştu: {e}")
