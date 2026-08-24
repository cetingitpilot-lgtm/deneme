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

# Tema Seçimi
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
    bollinger_color = 'rgba(41, 98, 255, 0.5)' # Açık temada mavi daha iyi görünür

# --- 2. GÜVENLİ VERİ ÇEKME FONKSİYONU ---
@st.cache_data(ttl=900)
def veri_cek(sembol, iv):
    donem = "60d" if iv in ["5m", "15m"] else "730d" if iv == "1h" else "max"
    df = yf.download(sembol, period=donem, interval=iv)
    
    if df.empty:
        return df
        
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    
    df = df.reset_index()
    df.columns = [str(c).lower() for c in df.columns]
    
    if 'datetime' in df.columns:
        df.rename(columns={'datetime': 'time'}, inplace=True)
    elif 'date' in df.columns:
        df.rename(columns={'date': 'time'}, inplace=True)
    
    df = df.dropna(subset=['open', 'high', 'low', 'close'])
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # KRİTİK: lightweight_charts python kütüphanesi Python datetime nesnelerini kullanmayı tercih eder.
    # String formatı alt panelleri (subchart) bozabiliyor. Bu yüzden datetime objesinde bırakıyoruz.
    df['time'] = pd.to_datetime(df['time'], utc=True).dt.tz_convert(None)
    df = df.drop_duplicates(subset=['time']).sort_values('time').reset_index(drop=True)
    
    return df

df = veri_cek(symbol, interval)

# --- 3. VERİ KONTROLÜ VE ÇİZİM ---
if not df.empty and len(df) > 30:
    st.markdown(f"### {symbol} • {secilen_tf_etiket.upper()}")
    
    # İNDİKATÖR HESAPLAMALARI
    bb = ta.bbands(df['close'], length=20, std=2)
    macd_calc = ta.macd(df['close'])
    stoch_calc = ta.stochrsi(df['close']) # Örnek olması için StochRSI da ekledim
    
    # ---------------------------------------------------------
    # TRADINGVIEW (LIGHTWEIGHT) CHART OLUŞTURMA
    # ---------------------------------------------------------
    
    # 1. Ana Grafik (Fiyat)
    chart = StreamlitChart(width=1100, height=500, toolbox=True)
    
    # Tema ayarları uygulama
    chart.layout(background_color=bg_color, text_color=text_color, font_size=12, font_family="Arial")
    chart.grid(vert_enabled=True, horz_enabled=True, color=grid_color)
    chart.crosshair(mode='normal', vert_color=crosshair_color, vert_style='dashed', horz_color=crosshair_color, horz_style='dashed')
    
    # Zaman çizelgesi ayarı (sağda boşluk bırak)
    chart.time_scale(right_offset=10, min_bar_spacing=2)

    # Temel fiyat verisi
    fiyat_verisi = df[['time', 'open', 'high', 'low', 'close', 'volume']].copy()
    chart.set(fiyat_verisi)
    
    # 2. Bollinger Bantları
    if bb is not None and not bb.empty:
        bbu_data = pd.DataFrame({'time': df['time'], 'BB_Ust': bb.iloc[:, 2]}).dropna()
        bbl_data = pd.DataFrame({'time': df['time'], 'BB_Alt': bb.iloc[:, 0]}).dropna()
        
        line_bbu = chart.create_line(name='BB_Ust', color=bollinger_color, style='solid', width=1)
        line_bbl = chart.create_line(name='BB_Alt', color=bollinger_color, style='solid', width=1)
        
        line_bbu.set(bbu_data)
        line_bbl.set(bbl_data)

    # 3. MACD Paneli (Osilatör)
    if macd_calc is not None and not macd_calc.empty:
        macd_pane = chart.create_subchart(width=1100, height=200, sync=True)
        
        # MACD Histogramı
        hist_data = pd.DataFrame({'time': df['time'], 'MACD_Hist': macd_calc.iloc[:, 1]}).dropna()
        
        # Temaya göre Histogram renkleri (Açık temada daha belirgin renkler)
        if tema_secimi == "Koyu (Dark)":
            hist_data['color'] = hist_data['MACD_Hist'].apply(lambda x: 'rgba(38, 166, 154, 0.8)' if x >= 0 else 'rgba(239, 83, 80, 0.8)')
        else:
             hist_data['color'] = hist_data['MACD_Hist'].apply(lambda x: 'rgba(7, 137, 125, 0.8)' if x >= 0 else 'rgba(209, 36, 33, 0.8)')
        
        hist_series = macd_pane.create_histogram(name='MACD_Hist')
        hist_series.set(hist_data)
        
        # MACD ve Sinyal Çizgileri
        macd_line_data = pd.DataFrame({'time': df['time'], 'MACD_Line': macd_calc.iloc[:, 0]}).dropna()
        signal_line_data = pd.DataFrame({'time': df['time'], 'Signal_Line': macd_calc.iloc[:, 2]}).dropna()
        
        macd_series = macd_pane.create_line(name='MACD_Line', color='#2962FF', width=2)
        signal_series = macd_pane.create_line(name='Signal_Line', color='#FF6D00', width=2)
        
        macd_series.set(macd_line_data)
        signal_series.set(signal_line_data)

    # 4. STOCH RSI Paneli (İkinci Osilatör Örneği)
    if stoch_calc is not None and not stoch_calc.empty:
        stoch_pane = chart.create_subchart(width=1100, height=150, sync=True)
        
        stoch_k_data = pd.DataFrame({'time': df['time'], 'Stoch_K': stoch_calc.iloc[:, 0]}).dropna()
        stoch_d_data = pd.DataFrame({'time': df['time'], 'Stoch_D': stoch_calc.iloc[:, 1]}).dropna()
        
        stoch_k = stoch_pane.create_line(name='Stoch_K', color='#2962FF', width=2)
        stoch_d = stoch_pane.create_line(name='Stoch_D', color='#FF6D00', width=2)
        
        stoch_k.set(stoch_k_data)
        stoch_d.set(stoch_d_data)

    # 5. Grafiği Göster
    chart.load()

elif df.empty:
    st.error("Veri çekilemedi. Borsa kapalı olabilir veya sembol hatalı.")
else:
    st.warning("Yeterli veri bulunamadı. Lütfen farklı bir sembol veya zaman dilimi deneyin.")
