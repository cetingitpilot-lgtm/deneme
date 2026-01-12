import streamlit as st
import yfinance as yf
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from indicators import MODULLER

st.set_page_config(page_title="Pro Terminal", layout="wide")

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

        x_axis = df.index.strftime("%d/%m %H:%M")

        # 1. Ana Fiyat (Hoversiz)
        fig.add_trace(go.Candlestick(
            x=x_axis, open=df['Open'], high=df['High'], 
            low=df['Low'], close=df['Close'], name="Fiyat",
            hoverinfo="none" 
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
            # Tüm indikatör hoverlarını kapat
            fig.data[-1].hoverinfo = "none"

        # --- SABİT BİLGİ PANELİ (HOVERLABEL YERİNE ANNOTATION) ---
        # Bu kısım TradingView'daki sol üst veri panelini simüle eder
        # 'x unified' hover aktif olduğunda tüm veriler tek bir annotation'a akacak
        
        fig.update_layout(
            hovermode="x unified",
            hoverdistance=-1, # Tüm X ekseninde yakala
            hoverlabel=dict(
                bgcolor="rgba(0,0,0,0.8)" if tema == "Siyah" else "rgba(255,255,255,0.8)",
                font_size=12,
                font_family="Courier New",
                font_color=metin_rengi,
                # BURASI SİHİRLİ NOKTA: Hover kutusunu sol üste sabitler
                xanchor="left",
                yanchor="top",
            )
        )

        # --- DİKEY ÇİZGİ VE TÜM EKSENLERİ BAĞLAMA ---
        fig.update_traces(xaxis="x")
        fig.update_xaxes(
            showspikes=True, spikemode="across", spikesnap="cursor",
            spikethickness=1, spikedash="dash", spikecolor="gray",
            showgrid=False, zeroline=False,
            # Kaydırmada eksen başlıklarının yer değiştirmesini engellemek için:
            fixedrange=False 
        )

        # --- GRAFİĞİN EN ÜSTÜNE SABİT ETİKETLER ---
        # Panel başlıkları (kaymayan tipte)
        current_row = 2
        for isim in secilenler:
            if MODULLER[isim].TYPE == "oscillator":
                fig.add_annotation(
                    xref="paper", yref=f"y{current_row} domain",
                    x=0.005, y=1.05, text=f"<b>{isim}</b>",
                    showarrow=False, font=dict(size=11, color=metin_rengi),
                    xanchor="left", yanchor="top", row=current_row, col=1
                )
                current_row += 1

        fig.update_layout(
            template="plotly_dark" if tema=="Siyah" else "plotly_white",
            paper_bgcolor=arkaplan, plot_bgcolor=arkaplan,
            height=400 + (len(osc_list)*200),
            xaxis_rangeslider_visible=False, xaxis_type='category',
            dragmode='pan', showlegend=False,
            margin=dict(r=80, l=10, t=50, b=50)
        )
        
        fig.update_yaxes(side="right", showgrid=True, gridcolor="rgba(128,128,128,0.1)")
        
        for i in range(1, toplam_satir):
            fig.update_xaxes(showticklabels=False, row=i, col=1)
        fig.update_xaxes(showticklabels=True, row=toplam_satir, col=1)

        # Streamlit üzerinde gösterirken Plotly config ayarlarını ekleyelim
        # Bu ayar, mouse'u takip eden kutuyu sol üstte tutmaya zorlar
        st.plotly_chart(fig, use_container_width=True, config={
            'scrollZoom': True,
            'displayModeBar': False,
        })
        
        st.markdown(
            """
            <style>
            /* Plotly hover kutusunu sol üst köşeye çivilemek için CSS */
            .hoverlayer {
                transform: translate(10px, 10px) !important;
                pointer-events: none !important;
            }
            </style>
            """, unsafe_allow_html=True
        )

except Exception as e:
    st.error(f"Hata oluştu: {e}")
