import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import importlib
import indicators
import os

st.set_page_config(layout="wide", page_title="Gemini Finansal Analiz")

# 1. VERİ ÇEKME
symbol = st.sidebar.text_input("Sembol (Örn: BTC-USD veya THYAO.IS)", "BTC-USD")
df = yf.download(symbol, period="1d", interval="15m")

if not df.empty:
    # 2. DİNAMİK İNDİKATÖR YÜKLEME
    overlay_mods = []
    oscillator_mods = []

    for ind_name in indicators.indicator_list:
        mod = importlib.import_module(f"indicators.{ind_name}")
        if hasattr(mod, 'BILGI'):
            if mod.BILGI["tip"] == "overlay":
                overlay_mods.append(mod)
            else:
                oscillator_mods.append(mod)

    # 3. GRAFİK YAPISI (Satır Sayısı Belirleme)
    num_oscs = len(oscillator_mods)
    # Fiyat alanı %60, diğerleri kalan alanı paylaşır
    row_heights = [0.6] + [0.4 / num_oscs] * num_oscs

    fig = make_subplots(
        rows=1 + num_oscs, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=row_heights
    )

    # 4. FİYAT (CANDLESTICK) ÇİZİMİ
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], 
        low=df['Low'], close=df['Close'], name="Fiyat"
    ), row=1, col=1)

    # 5. OVERLAY İNDİKATÖRLERİ (Fiyat Üstüne)
    for mod in overlay_mods:
        mod.çiz(fig, df, row=1)

    # 6. OSCILLATOR İNDİKATÖRLERİ (Alt Panellere)
    for i, mod in enumerate(oscillator_mods, start=2):
        mod.çiz(fig, df, row=i)
        
        # İSTEDİĞİN ÖZELLİK: Sabit Sol Üst Etiket
        fig.add_annotation(
            x=0, y=1, xref=f"x{i} domain", yref=f"y{i} domain",
            text=f"<b>{mod.BILGI['ad']}</b>", showarrow=False,
            xanchor="left", yanchor="top", font=dict(color="white", size=11),
            bgcolor="rgba(0,0,0,0.6)"
        )

    # 7. GLOBAL GÖRSEL AYARLAR (İstediğin Crosshair ve Sabit Hover)
    fig.update_layout(
        height=900,
        template="plotly_dark",
        hovermode="x unified", # Tüm bilgileri tek bir kutuda birleştirir
        showlegend=False,
        dragmode="pan", # Mouse ile kaydırma modu
        margin=dict(l=10, r=10, t=30, b=10),
        hoverlabel=dict(
            bgcolor="rgba(30, 30, 30, 0.9)",
            font_size=12,
            align="left"
        )
    )

    # Senkronize Dikey Çizgiler (Spikes)
    fig.update_xaxes(
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikedash="dash",
        spikecolor="#888888",
        spikethickness=1,
        rangeslider_visible=False
    )

    # Fiyat paneli için sabit başlık
    fig.add_annotation(
        x=0, y=1, xref="x1 domain", yref="y1 domain",
        text=f"<b>{symbol} - VERİ PANELİ</b>", showarrow=False,
        xanchor="left", yanchor="top", font=dict(color="#00FF00", size=13),
        bgcolor="rgba(0,0,0,0.8)"
    )

    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
else:
    st.error("Veri çekilemedi, lütfen sembolü kontrol edin.")
