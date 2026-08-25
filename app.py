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

# --- GÜVENLİ VERİ ÇEKME ---
@st.cache_data(ttl=900)
def veri_cek(sembol, iv):
    donem = "60d" if iv in ["5m", "15m"] else "730d" if iv == "1h" else "max"
    df = yf.download(sembol, period=donem, interval=iv)
    if df.empty: return pd.DataFrame()
    
    if isinstance(df.columns, pd.MultiIndex): 
        df.columns = [col[0] for col in df.columns]
    
    # İndeksi sütun yap
    df = df.reset_index()
    
    # Sütun isimlerini küçük harfe çevir
    df.columns = [str(c).lower() for c in df.columns]
    
    # GARANTİ ÇÖZÜM (KeyError için):
    # reset_index() sonrası tarih daima ilk sütundur (df.columns[0]).
    # İsmi ne olursa olsun, ilk sütunun adını zorla 'time' yapıyoruz.
    df.rename(columns={df.columns[0]: 'time'}, inplace=True)
        
    df = df.dropna(subset=['open', 'high', 'low', 'close'])
    
    # Zaman tipini timezone'suz güvenli datetime objesine çeviriyoruz
    df['time'] = pd.to_datetime(df['time'], utc=True).dt.tz_convert(None)
    
    # Günlük grafikse, kütüphane metin ('YYYY-MM-DD') formatı ister
    if iv == '1d':
        df['time'] = df['time'].dt.strftime('%Y-%m-%d')
    
    return df

df = veri_cek(symbol, interval)

# --- VERİ İŞLEME VE GRAFİK ÇİZİMİ ---
if not df.empty and len(df) > 30:
    st.markdown(f"### {symbol} • {secilen_tf_etiket.upper()}")
    
    # İndikatör Hesaplamaları
    bb = ta.bbands(df['close'], length=20, std=2)
    macd = ta.macd(df['close'])
    stoch = ta.stochrsi(df['close'])
    
    # Kütüphane ve Panelleri Oluştur
    chart = StreamlitChart(width=1100, height=800, inner_width=1, inner_height=0.5)
    macd_pane = chart.create_subchart(width=1, height=0.25, sync=True)
    stoch_pane = chart.create_subchart(width=1, height=0.25, sync=True)

    # --- TEMA VE RENK AYARLARI ---
    chart.layout(background_color=bg_color, text_color=text_color, font_size=12, font_family="Arial")
    chart.grid(vert_enabled=True, horz_enabled=True, color=grid_color)
    chart.crosshair(mode='normal', vert_color=crosshair_color, vert_style='dashed', horz_color=crosshair_color, horz_style='dashed')
    chart.time_scale(right_offset=10, min_bar_spacing=2)

    macd_pane.layout(background_color=bg_color, text_color=text_color, font_size=12, font_family="Arial")
    macd_pane.grid(vert_enabled=True, horz_enabled=True, color=grid_color)
    
    stoch_pane.layout(background_color=bg_color, text_color=text_color, font_size=12, font_family="Arial")
    stoch_pane.grid(vert_enabled=True, horz_enabled=True, color=grid_color)

    # --- VERİLERİ BAĞLAMA ---
    chart.set(df[['time', 'open', 'high', 'low', 'close', 'volume']])

    if bb is not None and not bb.empty:
        line_bbu = chart.create_line(color='rgba(136, 136, 136, 0.7)', width=1)
        line_bbl = chart.create_line(color='rgba(136, 136, 136, 0.7)', width=1)
        
        df_bbu = pd.DataFrame({'time': df['time'], 'value': bb.iloc[:, 2]}).dropna()
        df_bbl = pd.DataFrame({'time': df['time'], 'value': bb.iloc[:, 0]}).dropna()
        line_bbu.set(df_bbu)
        line_bbl.set(df_bbl)

    if macd is not None and not macd.empty:
        hist_series = macd_pane.create_histogram()
        macd_series = macd_pane.create_line(color='#2962FF', width=2)
        signal_series = macd_pane.create_line(color='#FF6D00', width=2)
        
        df_macd_line = pd.DataFrame({'time': df['time'], 'value': macd.iloc[:, 0]}).dropna()
        df_signal_line = pd.DataFrame({'time': df['time'], 'value': macd.iloc[:, 2]}).dropna()
        df_hist = pd.DataFrame({'time': df['time'], 'value': macd.iloc[:, 1]}).dropna()
        
        if tema_secimi == "Koyu (Dark)":
            df_hist['color'] = df_hist['value'].apply(lambda x: 'rgba(38, 166, 154, 0.8)' if x >= 0 else 'rgba(239, 83, 80, 0.8)')
        else:
            df_hist['color'] = df_hist['value'].apply(lambda x: 'rgba(7, 137, 125, 0.8)' if x >= 0 else 'rgba(209, 36, 33, 0.8)')
            
        hist_series.set(df_hist)
        macd_series.set(df_macd_line)
        signal_series.set(df_signal_line)

    if stoch is not None and not stoch.empty:
        stoch_k = stoch_pane.create_line(color='#2962FF', width=2)
        stoch_d = stoch_pane.create_line(color='#FF6D00', width=2)
        
        df_stoch_k = pd.DataFrame({'time': df['time'], 'value': stoch.iloc[:, 0]}).dropna()
        df_stoch_d = pd.DataFrame({'time': df['time'], 'value': stoch.iloc[:, 1]}).dropna()
        stoch_k.set(df_stoch_k)
        stoch_d.set(df_stoch_d)

    # Grafiği Ekrana Bas
    chart.load()

else:
    st.error("Yeterli veri bulunamadı. Lütfen sembolü kontrol edin.")
    
