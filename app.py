import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from lightweight_charts.widgets import StreamlitChart

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(layout="wide", page_title="Gemini Finansal Analiz (TV Engine)")

st.sidebar.header("Grafik Ayarları")
symbol = st.sidebar.text_input("Sembol", "BTC-USD")

timeframes = {"15 Dakika": "15m", "1 Saat": "1h", "1 Gün": "1d"}
secilen_tf_etiket = st.sidebar.selectbox("Zaman Dilimi", options=list(timeframes.keys()), index=0)
interval = timeframes[secilen_tf_etiket]

tema_secimi = st.sidebar.radio("Tema Seçimi", ["Koyu (Dark)", "Açık (Light)"], index=0)

# Renk Ayarları
if tema_secimi == "Koyu (Dark)":
    bg_color, text_color, grid_color, crosshair_color = '#131722', '#d1d4dc', '#2a2e39', '#787b86'
else:
    bg_color, text_color, grid_color, crosshair_color = '#ffffff', '#191919', '#e1e3e6', '#434651'

# --- VERİ ÇEKME VE TEMİZLEME ---
@st.cache_data(ttl=900)
def veri_cek(sembol, iv):
    donem = "60d" if iv in ["5m", "15m"] else "730d" if iv == "1h" else "max"
    df = yf.download(sembol, period=donem, interval=iv)
    if df.empty: return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex): df.columns = [col[0] for col in df.columns]
    
    df.columns = [str(c).lower() for c in df.columns]
    df = df.dropna(subset=['open', 'high', 'low', 'close'])
    return df

df_raw = veri_cek(symbol, interval)

if not df_raw.empty and len(df_raw) > 30:
    st.markdown(f"### {symbol} • {secilen_tf_etiket.upper()}")
    
    # --- 1. SIFIR HATA İÇİN VERİ HAZIRLIĞI ---
    # Zamanı JavaScript'in çökmeden okuyacağı garanti formata (String) çeviriyoruz
    zaman_serisi = (df_raw.index.tz_localize(None) if df_raw.index.tzinfo else df_raw.index).strftime('%Y-%m-%d %H:%M:%S')
    
    # Ana fiyat verisi
    fiyat_verisi = pd.DataFrame({
        'time': zaman_serisi,
        'open': df_raw['open'].astype(float),
        'high': df_raw['high'].astype(float),
        'low': df_raw['low'].astype(float),
        'close': df_raw['close'].astype(float),
        'volume': df_raw['volume'].astype(float) if 'volume' in df_raw.columns else 0.0
    })

    # --- 2. GRAFİK (CHART) VE YAPI OLUŞTURMA ---
    # Toplam yüksekliği 800px yapıyoruz ki alt paneller içerde kalsın ve taşmasın
    chart = StreamlitChart(width=1100, height=800)
    chart.layout(background_color=bg_color, text_color=text_color, font_size=12, font_family="Arial")
    chart.grid(vert_enabled=True, horz_enabled=True, color=grid_color)
    chart.crosshair(mode='normal', vert_color=crosshair_color, vert_style='dashed', horz_color=crosshair_color, horz_style='dashed')
    chart.time_scale(right_offset=10, min_bar_spacing=2)

    # Önce tüm panelleri ve çizgileri sisteme "tanıtıyoruz" (Daha veri basmadan)
    line_bbu = chart.create_line(color='rgba(136, 136, 136, 0.7)', width=1)
    line_bbl = chart.create_line(color='rgba(136, 136, 136, 0.7)', width=1)
    
    # Alt paneller: width=1 (tam genişlik), height=0.2 (toplamın %20'si)
    macd_pane = chart.create_subchart(width=1, height=0.2, sync=True)
    hist_series = macd_pane.create_histogram()
    macd_series = macd_pane.create_line(color='#2962FF', width=2)
    signal_series = macd_pane.create_line(color='#FF6D00', width=2)

    stoch_pane = chart.create_subchart(width=1, height=0.2, sync=True)
    stoch_k = stoch_pane.create_line(color='#2962FF', width=2)
    stoch_d = stoch_pane.create_line(color='#FF6D00', width=2)

    # --- 3. VERİLERİ (SET) BAĞLAMA ---
    # Ana veri bağlandı
    chart.set(fiyat_verisi)

    # Bollinger hesapla ve bağla (Sadece time ve value sütunları)
    bb = ta.bbands(df_raw['close'], length=20, std=2)
    if bb is not None and not bb.empty:
        df_bbu = pd.DataFrame({'time': zaman_serisi, 'value': bb.iloc[:, 2].astype(float)}).dropna()
        df_bbl = pd.DataFrame({'time': zaman_serisi, 'value': bb.iloc[:, 0].astype(float)}).dropna()
        line_bbu.set(df_bbu)
        line_bbl.set(df_bbl)

    # MACD hesapla ve bağla
    macd_calc = ta.macd(df_raw['close'])
    if macd_calc is not None and not macd_calc.empty:
        # MACD Line
        df_macd_line = pd.DataFrame({'time': zaman_serisi, 'value': macd_calc.iloc[:, 0].astype(float)}).dropna()
        macd_series.set(df_macd_line)
        
        # Signal Line
        df_signal_line = pd.DataFrame({'time': zaman_serisi, 'value': macd_calc.iloc[:, 2].astype(float)}).dropna()
        signal_series.set(df_signal_line)
        
        # Histogram (time, value, color)
        df_hist = pd.DataFrame({'time': zaman_serisi, 'value': macd_calc.iloc[:, 1].astype(float)}).dropna()
        if tema_secimi == "Koyu (Dark)":
            df_hist['color'] = df_hist['value'].apply(lambda x: 'rgba(38, 166, 154, 0.8)' if x >= 0 else 'rgba(239, 83, 80, 0.8)')
        else:
            df_hist['color'] = df_hist['value'].apply(lambda x: 'rgba(7, 137, 125, 0.8)' if x >= 0 else 'rgba(209, 36, 33, 0.8)')
        hist_series.set(df_hist)

    # Stoch RSI hesapla ve bağla
    stoch_calc = ta.stochrsi(df_raw['close'])
    if stoch_calc is not None and not stoch_calc.empty:
        df_stoch_k = pd.DataFrame({'time': zaman_serisi, 'value': stoch_calc.iloc[:, 0].astype(float)}).dropna()
        df_stoch_d = pd.DataFrame({'time': zaman_serisi, 'value': stoch_calc.iloc[:, 1].astype(float)}).dropna()
        stoch_k.set(df_stoch_k)
        stoch_d.set(df_stoch_d)

    # --- 4. GRAFİĞİ RENDER ET ---
    chart.load()

else:
    st.error("Yeterli veri bulunamadı. Lütfen sembolü kontrol edin.")
