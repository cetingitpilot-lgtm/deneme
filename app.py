import streamlit as st
import yfinance as yf
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from indicators import MODULLER

st.set_page_config(page_title="Pro Terminal", layout="wide")

# --- CSS SİHİRBAZLIĞI (BU KISIM ÇOK ÖNEMLİ) ---
# Bu kodlar Plotly'nin hareket mekanizmasını bozar ve kutuyu sol üste kilitler.
st.markdown("""
    <style>
    /* 1. Hover kutusunun (tooltip) yerini zorla sabitle */
    /* Streamlit içindeki grafik container'ını hedef alıyoruz */
    [data-testid="stPlotlyChart"] .js-plotly-plot .plotly .hoverlayer {
        transform: translate(10px, 0px) !important; /* Sol üst köşeye (10px içeriden) sabitle */
        position: absolute !important;
        top: 0px !important;
        left: 0px !important;
        z-index: 10000 !important;
        pointer-events: none !important; /* Mouse tıklamasını engelleme */
    }

    /* 2. Kutunun içindeki metinleri düzenle */
    [data-testid="stPlotlyChart"] .js-plotly-plot .plotly .hoverlayer .hovertext text {
        font-family: 'Monospace', monospace !important;
        font-size: 12px !important;
        font-weight: bold !important;
        fill: #ffffff !important; /* Yazı rengi (Beyaz) */
        text-shadow: 1px 1px 2px black !important; /* Okunabilirlik için gölge */
    }
    
    /* 3. Kutunun arkasındaki siyah fonu ve ok işaretini tamamen YOK ET */
    /* Sadece yazılar havada asılı kalsın */
    [data-testid="stPlotlyChart"] .js-plotly-plot .plotly .hoverlayer .hovertext path {
        fill: rgba(0,0,0,0) !important;
        stroke: none !important;
    }
    
    /* 4. Çizgi üzerindeki baloncukları gizle (sadece genel kutu kalsın) */
    [data-testid="stPlotlyChart"] .js-plotly-plot .plotly .hoverlayer .spikeline {
        display: none !important;
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
    
    # CSS içindeki yazı rengini temaya göre ayarla
    text_color = "white" if tema == "Siyah" else "black"
    st.markdown(f"""<style>
    [data-testid="stPlotlyChart"] .js-plotly-plot .plotly .hoverlayer .hovertext text {{
        fill: {text_color} !important;
    }}</style>""", unsafe_allow_html=True)
    
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

        # 1. Ana Fiyat (İsimlendirmeyi kısalttık)
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

        # Dikey Çizgi ve Eksen Ayarları
        fig.update_traces(xaxis="x")
        fig.update_xaxes(
            showspikes=True, spikemode="across", spikesnap="cursor",
            spikethickness=1, spikedash="dash", spikecolor="gray",
            showgrid=False, zeroline=False
        )

        # LAYOUT AYARLARI
        fig.update_layout(
            template="plotly_dark" if tema=="Siyah" else "plotly_white",
            paper_bgcolor=arkaplan, plot_bgcolor=arkaplan,
            height=600,
            xaxis_rangeslider_visible=False, xaxis_type='category',
            dragmode='pan', showlegend=False,
            margin=dict(r=50, l=10, t=10, b=10),
            
            # --- KRİTİK AYARLAR ---
            hovermode="x unified", # Tüm verileri birleştir
            hoverdistance=-1,      # Tüm dikey eksende yakala
            hoverlabel=dict(
                bgcolor="rgba(0,0,0,0)", # Plotly tarafında da şeffaflık verelim
                bordercolor="rgba(0,0,0,0)",
                namelength=-1,
                font=dict(family="Monospace"),
                align="left"
            )
        )
        
        fig.update_yaxes(side="right", showgrid=True, gridcolor="rgba(128,128,128,0.1)")
        
        # Gereksiz tarihleri gizle
        for i in range(1, toplam_satir):
            fig.update_xaxes(showticklabels=False, row=i, col=1)
        fig.update_xaxes(showticklabels=True, row=toplam_satir, col=1)

        st.plotly_chart(fig, width="stretch", config={'scrollZoom': True})

except Exception as e:
    st.error(f"Hata oluştu: {e}")

