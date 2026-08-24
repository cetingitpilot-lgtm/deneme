import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from lightweight_charts.widgets import StreamlitChart

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(layout="wide", page_title="Gemini Finansal Analiz (TV Engine)")

# --- 1. YAN PANEL (SIDEBAR) & AYARLAR ---
st.sidebar.header("Grafik Ayarları")
symbol = st.sidebar.text_input("Sembol (Örn: BTC-USD veya THYAO.IS)", "BTC-USD")

timeframes = {
    "15 Dakika": "15m",
    "1 Saat": "1h",
    "1 Gün": "1d"
}
secilen_tf_etiket = st.sidebar.selectbox("Zaman Dilimi", options=list(timeframes.keys()), index=0)
interval = timeframes[secilen_tf_etiket]

tema_secimi = st.sidebar.radio("Tema Seçimi", ["Koyu (Dark)", "Açık (Light)"], index=0)

# Temaya Göre Dinamik Renk Paleti Tanımlamaları
if tema_secimi == "Koyu (Dark)":
    bg_color = '#131722'
    text_color = '#d1d4dc'
    grid_color = '#2a2e39'
    crosshair_color = '#787b86'
    bollinger_color = 'rgba(136, 136, 136, 0.7)'
else:
    bg_color = '#ffffff'
    text_color = '#191919'
    grid_color = '#e1e3e6'
    crosshair_color = '#434651'
    bollinger_color = 'rgba(41, 98, 255, 0.5)' 

# --- 2. GÜVENLİ VERİ ÇEKME FONKSİYONU ---
@st.cache_data(ttl=900)
def veri_cek(sembol, iv):
    donem = "60d" if iv in ["5m", "15m"] else "730d" if iv == "1h" else "max"
    df = yf.download(sembol, period=donem, interval=iv)
    
    if df.empty:
        return pd.DataFrame()
        
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    
    df.columns = [str(c).lower() for c in df.columns]
    
    df = df.dropna(subset=['open', 'high', 'low', 'close'])
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

df_raw = veri_cek(symbol, interval)

# --- 3. VERİ KONTROLÜ VE ÇİZİM ---
if not df_raw.empty and len(df_raw) > 30:
    st.markdown(f"### {symbol} • {secilen_tf_etiket.upper()}")
    
    # KRİTİK: Zamanı string yapmak yerine ham datetime'da (tz-naive) bırakıyoruz. (Intraday desteği için şart)
    zaman_verisi = df_raw.index.tz_localize(None) if df_raw.index.tzinfo else df_raw.index
    
    fiyat_verisi = pd.DataFrame({
        'time': zaman_verisi,
        'open': df_raw['open'].values,
        'high': df_raw['high'].values,
        'low': df_raw['low'].values,
        'close': df_raw['close'].values,
        'volume': df_raw['volume'].values if 'volume' in df_raw.columns else [0] * len(df_raw)
    })
    
    # İndikatör Hesaplamaları
    bb = ta.bbands(df_raw['close'], length=20, std=2)
    macd_calc = ta.macd(df_raw['close'])
    stoch_calc = ta.stochrsi(df_raw['close'])
    
    # ---------------------------------------------------------
    # TRADINGVIEW (LIGHTWEIGHT) CHART OLUŞTURMA
    # ---------------------------------------------------------
    
    # Yüksekliği 800'e çıkarıyoruz ki alt panellere (osilatörlere) yer kalsın
    chart = StreamlitChart(width=1100, height=800, toolbox=True)
    
    chart.layout(background_color=bg_color, text_color=text_color, font_size=12, font_family="Arial")
    chart.grid(vert_enabled=True, horz_enabled=True, color=grid_color)
    chart.crosshair(mode='normal', vert_color=crosshair_color, vert_style='dashed', horz_color=crosshair_color, horz_style='dashed')
    chart.time_scale(right_offset=10, min_bar_spacing=2)

    chart.set(fiyat_verisi)
    
    # 2. Bollinger Bantları
    if bb is not None and not bb.empty:
        bb_df = pd.DataFrame({
            'time': zaman_verisi,
            'BB_Ust': bb.iloc[:, 2].values,
            'BB_Alt': bb.iloc[:, 0].values
        }).dropna()
        
        line_bbu = chart.create_line(name='BB_Ust', color=bollinger_color, style='solid', width=1)
        line_bbl = chart.create_line(name='BB_Alt', color=bollinger_color, style='solid', width=1)
        
        line_bbu.set(bb_df[['time', 'BB_Ust']])
        line_bbl.set(bb_df[['time', 'BB_Alt']])

    # 3. MACD Paneli (Osilatör)
    if macd_calc is not None and not macd_calc.empty:
        # KRİTİK DÜZELTME: height=200 yerine height=0.25 (toplam grafiğin %25'i) yapıldı
        macd_pane = chart.create_subchart(width=1, height=0.25, sync=True)
        
        macd_df = pd.DataFrame({
            'time': zaman_verisi,
            'MACD_Line': macd_calc.iloc[:, 0].values,
            'MACD_Hist': macd_calc.iloc[:, 1].values,
            'Signal_Line': macd_calc.iloc[:, 2].values
        }).dropna()
        
        if tema_secimi == "Koyu (Dark)":
            macd_df['color'] = macd_df['MACD_Hist'].apply(lambda x: 'rgba(38, 166, 154, 0.8)' if x >= 0 else 'rgba(239, 83, 80, 0.8)')
        else:
             macd_df['color'] = macd_df['MACD_Hist'].apply(lambda x: 'rgba(7, 137, 125, 0.8)' if x >= 0 else 'rgba(209, 36, 33, 0.8)')
        
        hist_series = macd_pane.create_histogram(name='MACD_Hist')
        macd_series = macd_pane.create_line(name='MACD_Line', color='#2962FF', width=2)
        signal_series = macd_pane.create_line(name='Signal_Line', color='#FF6D00', width=2)
        
        hist_series.set(macd_df[['time', 'MACD_Hist', 'color']])
        macd_series.set(macd_df[['time', 'MACD_Line']])
        signal_series.set(macd_df[['time', 'Signal_Line']])

    # 4. STOCH RSI Paneli (Osilatör)
    if stoch_calc is not None and not stoch_calc.empty:
        # KRİTİK DÜZELTME: height=0.20 (toplam grafiğin %20'si)
        stoch_pane = chart.create_subchart(width=1, height=0.20, sync=True)
        
        stoch_df = pd.DataFrame({
            'time': zaman_verisi,
            'Stoch_K': stoch_calc.iloc[:, 0].values,
            'Stoch_D': stoch_calc.iloc[:, 1].values
        }).dropna()
        
        stoch_k = stoch_pane.create_line(name='Stoch_K', color='#2962FF', width=2)
        stoch_d = stoch_pane.create_line(name='Stoch_D', color='#FF6D00', width=2)
        
        stoch_k.set(stoch_df[['time', 'Stoch_K']])
        stoch_d.set(stoch_df[['time', 'Stoch_D']])

    # 5. Grafiği Göster
    chart.load()

elif df_raw.empty:
    st.error("Veri çekilemedi. Borsa kapalı olabilir veya sembol hatalı.")
else:
    st.warning("Yeterli veri bulunamadı. Lütfen farklı bir sembol veya zaman dilimi deneyin.")
