import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta
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

# Tarih Aralığı Seçimi
bugun = datetime.now()
varsayilan_baslangic = bugun - timedelta(days=30)
tarih_araligi = st.sidebar.date_input("Tarih Aralığı", value=(varsayilan_baslangic, bugun), max_value=bugun)

# --- 2. VERİ ÇEKME FONKSİYONU ---
@st.cache_data(ttl=900)
def veri_cek(sembol, iv):
    donem = "60d" if iv in ["5m", "15m"] else "730d" if iv == "1h" else "max"
    df = yf.download(sembol, period=donem, interval=iv)
    
    if df.empty:
        return df
        
    # MultiIndex varsa düzleştir
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    
    # İndeksi sütuna taşı (time sütunu için)
    df = df.reset_index()
    
    # Tüm sütun adlarını küçük harfe çevir
    df.columns = [str(c).lower() for c in df.columns]
    
    # Tarih sütununun adını kesin olarak 'time' yap
    if 'datetime' in df.columns:
        df.rename(columns={'datetime': 'time'}, inplace=True)
    elif 'date' in df.columns:
        df.rename(columns={'date': 'time'}, inplace=True)
    
    # Eksikleri temizle ve sayısal tipe dönüştür
    df = df.dropna()
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()
    
    return df

df = veri_cek(symbol, interval)

# --- 3. TARİH FİLTRESİ ---
if not df.empty and len(tarih_araligi) == 2:
    baslangic_tarihi, bitis_tarihi = tarih_araligi
    df['time'] = pd.to_datetime(df['time']).dt.tz_localize(None)
    bitis_tarihi = pd.to_datetime(bitis_tarihi) + timedelta(days=1)
    
    mask = (df['time'] >= pd.to_datetime(baslangic_tarihi)) & (df['time'] <= bitis_tarihi)
    df = df.loc[mask]

# Veri uygunsa grafiği çiz
if not df.empty and len(df) > 30:
    st.markdown(f"### {symbol} • {secilen_tf_etiket.upper()}")
    
    # ---------------------------------------------------------
    # TRADINGVIEW (LIGHTWEIGHT) CHART OLUŞTURMA
    # ---------------------------------------------------------
    
    # 1. Ana Grafik (Fiyat)
    chart = StreamlitChart(width=1100, height=500, toolbox=True)
    
    # 2. Tema ve Görsel Ayarlar
    chart.layout(background_color='#131722', text_color='#d1d4dc', font_size=12, font_family="Arial")
    chart.grid(vert_enabled=True, horz_enabled=True, color='#2a2e39')
    chart.crosshair(mode='normal', vert_color='#787b86', vert_style='dashed', horz_color='#787b86', horz_style='dashed')
    chart.time_scale(right_offset=5, min_bar_spacing=2)

    # 3. Mum Verisini Ekle
    chart.set(df)
    
    # 4. Bollinger Bantları
    bb = ta.bbands(df['close'], length=20, std=2)
    if bb is not None and not bb.empty:
        # KRİTİK DÜZELTME: Sütun adları create_line içindeki name ile birebir aynı olmalı
        bbu_data = pd.DataFrame({'time': df['time'], 'BB_Ust': bb.iloc[:, 2]})
        bbl_data = pd.DataFrame({'time': df['time'], 'BB_Alt': bb.iloc[:, 0]})
        
        line_bbu = chart.create_line(name='BB_Ust', color='rgba(136, 136, 136, 0.7)', style='solid', width=1)
        line_bbl = chart.create_line(name='BB_Alt', color='rgba(136, 136, 136, 0.7)', style='solid', width=1)
        
        line_bbu.set(bbu_data)
        line_bbl.set(bbl_data)

    # 5. MACD Alt Paneli (Subchart)
    macd_calc = ta.macd(df['close'])
    if macd_calc is not None and not macd_calc.empty:
        macd_pane = chart.create_subchart(width=1100, height=200, sync=True)
        
        # MACD Histogramı
        hist_data = pd.DataFrame({
            'time': df['time'], 
            'MACD_Hist': macd_calc.iloc[:, 1]
        })
        hist_data['color'] = hist_data['MACD_Hist'].apply(
            lambda x: 'rgba(38, 166, 154, 0.8)' if x >= 0 else 'rgba(239, 83, 80, 0.8)'
        )
        
        hist_series = macd_pane.create_histogram(name='MACD_Hist')
        hist_series.set(hist_data)
        
        # MACD ve Sinyal Çizgileri
        macd_line_data = pd.DataFrame({'time': df['time'], 'MACD_Line': macd_calc.iloc[:, 0]})
        signal_line_data = pd.DataFrame({'time': df['time'], 'Signal_Line': macd_calc.iloc[:, 2]})
        
        macd_series = macd_pane.create_line(name='MACD_Line', color='#2962FF', width=2)
        signal_series = macd_pane.create_line(name='Signal_Line', color='#FF6D00', width=2)
        
        macd_series.set(macd_line_data)
        signal_series.set(signal_line_data)

    # 6. Grafiği Yükle
    chart.load()

elif df.empty:
    st.error("Veri çekilemedi. Borsa kapalı olabilir veya sembol hatalı.")
else:
    st.warning("Seçili tarih aralığında yeterli veri bulunamadı.")
