import streamlit as st
import yfinance as yf
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from indicators import MODULLER

st.set_page_config(page_title="Pro Terminal", layout="wide")

# --- CSS İLE ZORLA SABİTLEME ---
# Bu kısım Plotly'nin hesaplamalarını ezip hover kutusunu sol üste kilitler
st.markdown("""
    <style>
    /* Hover kutusunun (tooltip) ana taşıyıcısını yakala */
    .js-plotly-plot .plotly .hoverlayer {
        position: absolute !important;
        top: 0px !important;
        left: 0px !important;
        transform: translate(10px, 0px) !important; /* Sol üstten biraz boşluk */
        pointer-events: none !important;
        z-index: 1000 !important;
    }

    /* Hover kutusunun içindeki metin hizalaması */
    .js-plotly-plot .plotly .hoverlayer .hovertext {
        text-anchor: start !important; /* Yazıyı sola yasla */
    }

    /* Kutunun arkasındaki siyah/beyaz fonu ve oku kaldır (Sadece yazı kalsın) */
    .js-plotly-plot .plotly .hoverlayer .hovertext path {
        fill: rgba(0,0,0,0) !important; /* Arkaplanı tamamen şeffaf yap */
        stroke: none !important;        /* Çerçeve çizgisini kaldır */
    }
    
    /* Yazıların okunabilirliğini artır (gölge ekle) */
    .js-plotly-plot .plotly .hoverlayer .hovertext text {
        text-shadow: 1px 1px 1px rgba(0,0,0,0.8) !important;
        font-family: 'Courier New', monospace !important;
        font-weight: bold !important;
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
    
    st.divider()
    secilenler = st.multiselect("İndikatörler", list(MODULLER.keys()), default=["EMA 7", "RSI"])

try:
    df = yf.download(hisse, period=periyot, interval=zaman)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        osc_list = [i for i in secilenler if MODULLER[i].TYPE == "oscillator"]
        toplam_satir = 1 + len(osc_list)
        satir_oranlari = [0.6] + [0.4/len(osc_list) if osc_list else 0] * len(osc_list)

        fig = make_subplots(rows=toplam_satir, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, row_heights=satir_oranlari)

        x_axis = df.index.strftime("%d/%m %H:%M")

        # 1. Ana Fiyat
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

        # Dikey Çizgi Ayarları
        fig.update_traces(xaxis="x")
        fig.update_xaxes(
            showspikes=True, spikemode="across", spikesnap="cursor",
            spikethickness=1, spikedash="dash", spikecolor="gray",
            showgrid=False, zeroline=False
        )

        # GRAFİK DÜZENİ
        fig.update_layout(
            template="plotly_dark" if tema=="Siyah" else "plotly_white",
            paper_bgcolor=arkaplan, plot_bgcolor=arkaplan,
            height=600,
            xaxis_rangeslider_visible=False, xaxis_type='category',
            dragmode='pan', showlegend=False,
            margin=dict(r=50, l=10, t=10, b=10),
            
            # --- ÖNEMLİ KISIM: HOVER MODU ---
            hovermode="x unified", # Tüm verileri tek listede topla
            hoverlabel=dict(
                # CSS ile bunları ezeceğiz ama yine de varsayılanı ayarlayalım
                bgcolor="rgba(0,0,0,0)", 
                bordercolor="rgba(0,0,0,0)",
                font_size=13,
                font_family="Monospace",
                align="left",
                namelength=-1 # İsimleri tam göster
            )
        )
        
        fig.update_yaxes(side="right", showgrid=True, gridcolor="rgba(128,128,128,0.1)")

        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

except Exception as e:
    st.error(f"Hata oluştu: {e}")
