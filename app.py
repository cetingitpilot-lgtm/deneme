import streamlit as st
import yfinance as yf
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from indicators import MODULLER

st.set_page_config(page_title="Pro Terminal", layout="wide")

# Sidebar Ayarları
with st.sidebar:
    st.header("📊 Kontrol")
    hisse = st.text_input("Hisse", "AAPL").upper()
    periyot = st.selectbox("Geçmiş", ["1mo", "3mo", "6mo", "1y", "5y"], index=2)
    zaman = st.selectbox("Dilim", ["1d", "1h", "1wk"], index=0)
    tema = st.radio("Tema", ["Siyah", "Beyaz"])
    arkaplan = "#0e1117" if tema == "Siyah" else "white"
    metin_rengi = "white" if tema == "Siyah" else "black"
    
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

        # X ekseni formatı
        x_axis = df.index.strftime("%d/%m %H:%M")

        # 1. Ana Fiyat (Mumlar)
        fig.add_trace(go.Candlestick(
            x=x_axis, open=df['Open'], high=df['High'], 
            low=df['Low'], close=df['Close'], name="Fiyat",
            # Hover kutusunuTradingView stili yapmak için:
            hovertemplate="A:%{open:.2f} Y:%{high:.2f} D:%{low:.2f} K:%{close:.2f}<extra></extra>"
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

        # --- DİKEY ÇİZGİYİ (SPIKE) GERİ GETİRME VE SENKRONİZE ETME ---
        fig.update_traces(xaxis="x") # Tüm izleri ana X eksenine bağla (Kritik!)
        
        fig.update_xaxes(
            showspikes=True,
            spikemode="across", # Tüm panelleri kesen çizgi
            spikesnap="cursor",
            spikethickness=1,
            spikedash="dash",
            spikecolor="#888",
            showgrid=False,
            zeroline=False,
            rangeslider_visible=False
        )

        # --- SOL ÜST KÖŞEDE SABİT İSİMLER ---
        # Her panelin sol üstüne ismini 'paper' koordinatıyla çiviliyoruz
        current_osc_row = 2
        for isim in secilenler:
            if MODULLER[isim].TYPE == "oscillator":
                fig.add_annotation(
                    xref="paper", yref=f"y{current_osc_row} domain",
                    x=0.005, y=0.98, text=f"<b>{isim}</b>",
                    showarrow=False, font=dict(size=11, color=metin_rengi),
                    xanchor="left", yanchor="top"
                )
                current_osc_row += 1
        
        # Ana grafik için isim
        fig.add_annotation(
            xref="paper", yref="y domain",
            x=0.005, y=0.98, text=f"<b>{hisse} - OHLC</b>",
            showarrow=False, font=dict(size=12, color=metin_rengi),
            xanchor="left", yanchor="top"
        )

        # GENEL GÖRÜNÜM AYARLARI
        fig.update_layout(
            template="plotly_dark" if tema=="Siyah" else "plotly_white",
            paper_bgcolor=arkaplan,
            plot_bgcolor=arkaplan,
            height=400 + (len(osc_list)*200),
            dragmode='pan',
            showlegend=False,
            hovermode="x", # "x unified" yerine sadece "x" dikey çizgiyi daha stabil kılar
            spikedistance=-1, # Çizginin her zaman aktif kalmasını sağlar
            margin=dict(r=60, l=10, t=30, b=50),
            
            # Hover kutusunu sol üste sabitlemeyi deneyen en hafif ayar
            hoverlabel=dict(
                bgcolor="rgba(0,0,0,0.6)",
                font_size=12,
                font_family="Monospace",
                align="left"
            )
        )
        
        fig.update_yaxes(side="right", showgrid=True, gridcolor="rgba(128,128,128,0.1)")
        
        # X ekseni etiketlerini sadece en altta göster
        for i in range(1, toplam_satir):
            fig.update_xaxes(showticklabels=False, row=i, col=1)
        fig.update_xaxes(showticklabels=True, row=toplam_satir, col=1)

        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

except Exception as e:
    st.error(f"Hata oluştu: {e}")
