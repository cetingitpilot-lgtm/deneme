import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import importlib
import indicators
import pandas as pd

st.set_page_config(layout="wide", page_title="Gemini Finansal Analiz")

# 1. VERİ ÇEKME
symbol = st.sidebar.text_input("Sembol (Örn: BTC-USD veya THYAO.IS)", "BTC-USD")

@st.cache_data(ttl=900)
def veri_cek(sembol):
    # Veriyi çek
    df = yf.download(sembol, period="1d", interval="15m")
    
    if df.empty:
        return df
        
    # KRİTİK DÜZELTME: MultiIndex varsa tamamen düzleştir
    if isinstance(df.columns, pd.MultiIndex):
        # Eğer yfinance ('Close', 'BTC-USD') şeklinde döndürüyorsa sadece ilk kelimeyi al ('Close')
        df.columns = [col[0] for col in df.columns]
    
    # Tüm harfleri ilk harfi büyük formata zorla (açıkça Open, High, Low, Close, Volume olduğundan emin olmak için)
    df.columns = [str(c).capitalize() for c in df.columns]
    
    # Eksik verileri (NaN) temizle
    df = df.dropna()
    
    # Tüm sütunların float tipinde olduğundan emin ol
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # Dönüşüm sonrası tekrar oluşabilecek NaN'ları at
    df = df.dropna()
    
    return df

# Veriyi çekelim
df = veri_cek(symbol)

# Bollinger (20) ve MACD (26) için en az 26 satır veri şarttır
if not df.empty and len(df) > 30:
    # 2. DİNAMİK İNDİKATÖR YÜKLEME
    overlay_mods = []
    oscillator_mods = []

    for ind_name in indicators.indicator_list:
        try:
            mod = importlib.import_module(f"indicators.{ind_name}")
            if hasattr(mod, 'BILGI'):
                if mod.BILGI["tip"] == "overlay":
                    overlay_mods.append(mod)
                else:
                    oscillator_mods.append(mod)
        except Exception as e:
            st.sidebar.error(f"{ind_name} yüklenirken hata: {str(e)}")

    # 3. GRAFİK YAPISI
    num_oscs = len(oscillator_mods)
    
    if num_oscs > 0:
        row_heights = [0.6] + [0.4 / num_oscs] * num_oscs
    else:
        row_heights = [1.0]

    fig = make_subplots(
        rows=1 + num_oscs, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=row_heights
    )

    # 4. FİYAT ÇİZİMİ
    fig.add_trace(
        go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], 
            low=df['Low'], close=df['Close'], name="Fiyat"
        ), 
        row=1, col=1
    )

    # 5. OVERLAY İNDİKATÖRLERİ
    for mod in overlay_mods:
        try:
            mod.çiz(fig, df, row=1)
        except Exception as e:
            st.sidebar.warning(f"{mod.BILGI['ad']} hata verdi: {str(e)}")

    # 6. OSCILLATOR İNDİKATÖRLERİ
    for i, mod in enumerate(oscillator_mods, start=2):
        try:
            mod.çiz(fig, df, row=i)
            
            # KRİTİK DÜZELTME: xref="x1 domain" yerine direkt figure add_annotation
            fig.add_annotation(
                text=f"<b>{mod.BILGI['ad']}</b>",
                xref=f"x{i} domain", yref=f"y{i} domain",
                x=0.01, y=0.95, showarrow=False,
                xanchor="left", yanchor="top", 
                font=dict(color="white", size=11),
                bgcolor="rgba(0,0,0,0.6)"
            )
        except Exception as e:
            st.sidebar.warning(f"{mod.BILGI['ad']} hata verdi: {str(e)}")

    # 7. GLOBAL GÖRSEL AYARLAR
    fig.update_layout(
        height=900,
        template="plotly_dark",
        hovermode="x unified",
        showlegend=False,
        dragmode="pan",
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_rangeslider_visible=False
    )

    # KRİTİK DÜZELTME: xref="x1 domain" hatasını yaratan asıl yer burasıydı.
    # xref="paper" ve yref="paper" kullanarak tüm eksen bağımlılıklarını kaldırdık.
    fig.add_annotation(
        text=f"<b>{symbol} - VERİ PANELİ</b>",
        xref="paper", yref="paper",
        x=0.01, y=0.99, showarrow=False,
        xanchor="left", yanchor="top", 
        font=dict(color="#00FF00", size=13),
        bgcolor="rgba(0,0,0,0.8)"
    )

    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

elif df.empty:
    st.error("Veri çekilemedi. Borsa kapalı olabilir veya sembol hatalı.")
else:
    st.warning(f"Seçili sembol için yeterli veri yok. ({len(df)} bar bulundu, en az 30 bar gerekli.)")
