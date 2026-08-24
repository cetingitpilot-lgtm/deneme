import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from lightweight_charts.widgets import StreamlitChart

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(layout="wide", page_title="Gemini Finansal Analiz (TV Engine)")

# --- 1. YAN PANEL (SIDEBAR) ---
st.sidebar.header("Grafik Ayarları")
symbol = st.sidebar.text_input("Sembol (Örn: BTC-USD veya THYAO.IS)", "BTC-USD")

timeframes = {
    "15 Dakika": "15m",
    "1 Saat": "1h",
    "1 Gün": "1d"
}
secilen_tf_etiket = st.sidebar.selectbox("Zaman Dilimi", options=list(timeframes.keys()), index=0)
interval = timeframes[secilen_tf_etiket]

# --- 2. GÜVENLİ VERİ ÇEKME FONKSİYONU ---
@st.cache_data(ttl=900)
def veri_cek(sembol, iv):
    donem = "60d" if iv in ["5m", "15m"] else "730d" if iv == "1h" else "max"
    df = yf.download(sembol, period=donem, interval=iv)
    
    if df.empty:
        return df
        
    # MultiIndex düzeltmesi
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    
    df = df.reset_index()
    df.columns = [str(c).lower() for c in df.columns]
    
    if 'datetime' in df.columns:
        df.rename(columns={'datetime': 'time'}, inplace=True)
    elif 'date' in df.columns:
        df.rename(columns={'date': 'time'}, inplace=True)
    
    # Eksikleri temizle ve sayısal tipe zorla
    df = df.dropna(subset=['open', 'high', 'low', 'close'])
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Zaman verisini kesinleştir ve sırala
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
    
    # Zamanı JavaScript için String'e çevir (Tüm hesaplamalardan SONRA yapılmalı)
    df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # ---------------------------------------------------------
    # TRADINGVIEW (LIGHTWEIGHT) CHART OLUŞTURMA
    # ---------------------------------------------------------
    
    # 1. Ana Grafik (Fiyat)
    chart = StreamlitChart(width=1100, height=500, toolbox=True)
    chart.layout(background_color='#131722', text_color='#d1d4dc', font_size=12, font_family="Arial")
    chart.grid(vert_enabled=True, horz_enabled=True, color='#2a2e39')
    chart.crosshair(mode='normal', vert_color='#787b86', vert_style='dashed', horz_color='#787b86', horz_style='dashed')
    chart.time_scale(right_offset=5, min_bar_spacing=2)

    # Temel fiyat verisi
    fiyat_verisi = df[['time', 'open', 'high', 'low', 'close', 'volume']].copy()
    chart.set(fiyat_verisi)
    
    # 2. Bollinger Bantları
    if bb is not None and not bb.empty:
        bbu_data = pd.DataFrame({'time': df['time'], 'BB_Ust': bb.iloc[:, 2]}).dropna()
        bbl_data = pd.DataFrame({'time': df['time'], 'BB_Alt': bb.iloc[:, 0]}).dropna()
        
        line_bbu = chart.create_line(name='BB_Ust', color='rgba(136, 136, 136, 0.7)', style='solid', width=1)
        line_bbl = chart.create_line(name='BB_Alt', color='rgba(136, 136, 136, 0.7)', style='solid', width=1)
        
        line_bbu.set(bbu_data)
        line_bbl.set(bbl_data)

    # 3. MACD Paneli
    if macd_calc is not None and not macd_calc.empty:
        macd_pane = chart.create_subchart(width=1100, height=200, sync=True)
        
        # MACD Histogramı
        hist_data = pd.DataFrame({'time': df['time'], 'MACD_Hist': macd_calc.iloc[:, 1]}).dropna()
        hist_data['color'] = hist_data['MACD_Hist'].apply(
            lambda x: 'rgba(38, 166, 154, 0.8)' if x >= 0 else 'rgba(239, 83, 80, 0.8)'
        )
        
        hist_series = macd_pane.create_histogram(name='MACD_Hist')
        hist_series.set(hist_data)
        
        # MACD ve Sinyal Çizgileri
        macd_line_data = pd.DataFrame({'time': df['time'], 'MACD_Line': macd_calc.iloc[:, 0]}).dropna()
        signal_line_data = pd.DataFrame({'time': df['time'], 'Signal_Line': macd_calc.iloc[:, 2]}).dropna()
        
        macd_series = macd_pane.create_line(name='MACD_Line', color='#2962FF', width=2)
        signal_series = macd_pane.create_line(name='Signal_Line', color='#FF6D00', width=2)
        
        macd_series.set(macd_line_data)
        signal_series.set(signal_line_data)

    # 4. Grafiği Göster
    chart.load()

elif df.empty:
    st.error("Veri çekilemedi. Borsa kapalı olabilir veya sembol hatalı.")
else:
    st.warning("Yeterli veri bulunamadı. Lütfen farklı bir sembol veya zaman dilimi deneyin.")
