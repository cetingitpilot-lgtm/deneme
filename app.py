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

# --- RENK AYARLARI ---
if tema_secimi == "Koyu (Dark)":
    bg_color, text_color, grid_color, crosshair_color = '#131722', '#d1d4dc', '#2a2e39', '#787b86'
else:
    bg_color, text_color, grid_color, crosshair_color = '#ffffff', '#191919', '#e1e3e6', '#434651'

# --- 1. GÜVENLİ VE KESİN VERİ ÇEKME ---
@st.cache_data(ttl=900)
def veri_cek(sembol, iv):
    # Yahoo Finance'in ASLA reddetmediği standart periyot terimleri
    if iv in ["1m", "5m", "15m"]:
        donem = "1mo"  # 15 dakikalık grafikler için 1 Ay
    elif iv == "1h":
        donem = "1y"   # Saatlik grafikler için 1 Yıl
    else:
        donem = "max"  # Günlük grafikler için Maksimum

    # Daha stabil olan Ticker.history() metodunu kullanıyoruz
    try:
        ticker = yf.Ticker(sembol)
        df = ticker.history(period=donem, interval=iv)
    except:
        return pd.DataFrame()

    # Eğer history() boş dönerse, yf.download ile son bir kurtarma denemesi yap
    if df.empty:
        df = yf.download(sembol, period=donem, interval=iv, progress=False)
        
    if df.empty:
        return pd.DataFrame()
        
    # MultiIndex (Karmaşık Sütun) temizliği
    if isinstance(df.columns, pd.MultiIndex): 
        df.columns = [col[0] for col in df.columns]
    
    # İndeksi sütun yap ve tüm harfleri küçült
    df = df.reset_index()
    df.columns = [str(c).lower() for c in df.columns]
    
    # İlk sütun daima tarihtir, adını kesin olarak 'time' yap
    df.rename(columns={df.columns[0]: 'time'}, inplace=True)
    
    # Boş verileri at ve float'a çevir
    df = df.dropna(subset=['open', 'high', 'low', 'close'])
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)
            
    # ZAMAN FORMATI DÜZELTME (JavaScript Çökmesini Engeller)
    df['time'] = pd.to_datetime(df['time'])
    
    # Günlük grafiklerde sadece Tarih (YYYY-MM-DD)
    if iv == '1d':
        df['time'] = df['time'].dt.strftime('%Y-%m-%d')
    # Saatlik/Dakikalık grafiklerde Tarih + Saat (YYYY-MM-DD HH:MM:SS)
    else:
        df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return df

df = veri_cek(symbol, interval)

# --- 2. VERİ İŞLEME VE GRAFİK ÇİZİMİ ---
if not df.empty and len(df) > 30:
    st.markdown(f"### {symbol} • {secilen_tf_etiket.upper()}")
    
    # İndikatör Hesaplamaları
    bb = ta.bbands(df['close'], length=20, std=2)
    macd = ta.macd(df['close'])
    stoch = ta.stochrsi(df['close'])
    
    # --- KÜTÜPHANE VE PANELLERİ OLUŞTUR ---
    # inner_height=0.5 -> Ana grafiğe %50 alan verir, alt panellerin görünmesini sağlar
    chart = StreamlitChart(width=1100, height=800, inner_width=1, inner_height=0.5)
    macd_pane = chart.create_subchart(width=1, height=0.25, sync=True)
    stoch_pane = chart.create_subchart(width=1, height=0.25, sync=True)

    # --- TEMA VE RENKLERİ UYGULA (HER PANELE AYRI AYRI) ---
    chart.layout(background_color=bg_color, text_color=text_color, font_size=12, font_family="Arial")
    chart.grid(vert_enabled=True, horz_enabled=True, color=grid_color)
    chart.crosshair(mode='normal', vert_color=crosshair_color, vert_style='dashed', horz_color=crosshair_color, horz_style='dashed')
    chart.time_scale(right_offset=10, min_bar_spacing=2)

    macd_pane.layout(background_color=bg_color, text_color=text_color, font_size=12, font_family="Arial")
    macd_pane.grid(vert_enabled=True, horz_enabled=True, color=grid_color)
    
    stoch_pane.layout(background_color=bg_color, text_color=text_color, font_size=12, font_family="Arial")
    stoch_pane.grid(vert_enabled=True, horz_enabled=True, color=grid_color)

    # --- VERİLERİ GRAFİĞE BAĞLA (.set) ---
    # Ana Fiyat Grafiği
    df_fiyat = df[['time', 'open', 'high', 'low', 'close', 'volume']]
    chart.set(df_fiyat)

    # Bollinger Bantları
    if bb is not None and not bb.empty:
        line_bbu = chart.create_line(color='rgba(136, 136, 136, 0.7)', width=1)
        line_bbl = chart.create_line(color='rgba(136, 136, 136, 0.7)', width=1)
        
        df_bbu = pd.DataFrame({'time': df['time'], 'value': bb.iloc[:, 2].astype(float)}).dropna()
        df_bbl = pd.DataFrame({'time': df['time'], 'value': bb.iloc[:, 0].astype(float)}).dropna()
        
        line_bbu.set(df_bbu)
        line_bbl.set(df_bbl)

    # MACD Alt Paneli
    if macd is not None and not macd.empty:
        hist_series = macd_pane.create_histogram()
        macd_series = macd_pane.create_line(color='#2962FF', width=2)
        signal_series = macd_pane.create_line(color='#FF6D00', width=2)
        
        df_macd_line = pd.DataFrame({'time': df['time'], 'value': macd.iloc[:, 0].astype(float)}).dropna()
        df_signal_line = pd.DataFrame({'time': df['time'], 'value': macd.iloc[:, 2].astype(float)}).dropna()
        df_hist = pd.DataFrame({'time': df['time'], 'value': macd.iloc[:, 1].astype(float)}).dropna()
        
        if tema_secimi == "Koyu (Dark)":
            df_hist['color'] = df_hist['value'].apply(lambda x: 'rgba(38, 166, 154, 0.8)' if x >= 0 else 'rgba(239, 83, 80, 0.8)')
        else:
            df_hist['color'] = df_hist['value'].apply(lambda x: 'rgba(7, 137, 125, 0.8)' if x >= 0 else 'rgba(209, 36, 33, 0.8)')
            
        hist_series.set(df_hist)
        macd_series.set(df_macd_line)
        signal_series.set(df_signal_line)

    # STOCH RSI Alt Paneli
    if stoch is not None and not stoch.empty:
        stoch_k = stoch_pane.create_line(color='#2962FF', width=2)
        stoch_d = stoch_pane.create_line(color='#FF6D00', width=2)
        
        df_stoch_k = pd.DataFrame({'time': df['time'], 'value': stoch.iloc[:, 0].astype(float)}).dropna()
        df_stoch_d = pd.DataFrame({'time': df['time'], 'value': stoch.iloc[:, 1].astype(float)}).dropna()
        
        stoch_k.set(df_stoch_k)
        stoch_d.set(df_stoch_d)

    # Grafiği Ekrana Bas
    chart.load()

else:
    st.error("Veri çekilemedi veya seçili zaman dilimi için yeterli veri bulunamadı. Lütfen sembolü kontrol edin.")
