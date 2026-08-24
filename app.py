import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from lightweight_charts.widgets import StreamlitChart # YENİ KÜTÜPHANE

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
    
    if df.empty: return df
        
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    
    df.columns = [str(c).capitalize() for c in df.columns]
    df = df.dropna()
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()
    
    # LIGHTWEIGHT CHARTS İÇİN KRİTİK VERİ YAPISI
    # İndeks "time" adında bir sütun olmak ZORUNDA.
    df.reset_index(inplace=True)
    
    # Sütun adını standart 'time' veya 'Date' yapıyoruz
    if 'Datetime' in df.columns:
        df.rename(columns={'Datetime': 'time'}, inplace=True)
    elif 'Date' in df.columns:
        df.rename(columns={'Date': 'time'}, inplace=True)
    
    return df

df = veri_cek(symbol, interval)

# --- 3. TARİH FİLTRESİ ---
if not df.empty and len(tarih_araligi) == 2:
    baslangic_tarihi, bitis_tarihi = tarih_araligi
    df['time'] = df['time'].dt.tz_localize(None) 
    bitis_tarihi = bitis_tarihi + timedelta(days=1)
    mask = (df['time'] >= pd.to_datetime(baslangic_tarihi)) & (df['time'] <= pd.to_datetime(bitis_tarihi))
    df = df.loc[mask]

# Veri uygunsa grafiği çiz
if not df.empty and len(df) > 30:
    st.markdown(f"### {symbol} - {secilen_tf_etiket.upper()}")
    
    # ---------------------------------------------------------
    # TRADINGVIEW (LIGHTWEIGHT) CHART OLUŞTURMA
    # ---------------------------------------------------------
    
    # 1. Ana Grafik (Fiyat) Nesnesini Oluştur
    # inner_width ve inner_height ile boyutları belirliyoruz
    chart = StreamlitChart(width=1000, height=500, toolbox=True)
    
    # 2. Grafik Temasını ve Davranışlarını Ayarla
    chart.layout(background_color='#131722', text_color='#d1d4dc', font_size=12, font_family="Arial")
    chart.grid(vert_enabled=True, horz_enabled=True, color='#2a2e39')
    chart.crosshair(mode='normal', vert_color='#787b86', vert_style='dashed', horz_color='#787b86', horz_style='dashed')
    
    # Zaman eksenini yapılandır (Gapless görünüm otomatik gelir)
    chart.time_scale(right_offset=5, min_bar_spacing=2)

    # 3. Mum Grafiğini Veriyle Besle
    chart.set(df)
    
    # 4. İndikatörleri Hesapla ve Ekle (Lightweight Charts'ta çizgi eklemek)
    # NOT: Pandas TA kullanmaya devam edebilirsiniz.
    import pandas_ta as ta
    
    # --- BOLLINGER BANTLARI (Fiyat grafiğinin üzerine) ---
    bb = ta.bbands(df['Close'], length=20, std=2)
    if bb is not None and not bb.empty:
        # Bollinger datası için 'time' ve 'value' formatında sözlükler oluşturmalıyız
        bbu = pd.DataFrame({'time': df['time'], 'value': bb.iloc[:, 2]}) # Üst Bant
        bbl = pd.DataFrame({'time': df['time'], 'value': bb.iloc[:, 0]}) # Alt Bant
        
        # Çizgileri ana grafiğe ekle
        line_bbu = chart.create_line(color='rgba(136, 136, 136, 0.7)', style='solid', width=1, name='BB Üst')
        line_bbl = chart.create_line(color='rgba(136, 136, 136, 0.7)', style='solid', width=1, name='BB Alt')
        
        line_bbu.set(bbu)
        line_bbl.set(bbl)

    # --- MACD İÇİN ALT PANEL OLUŞTURMA (SUB-CHART) ---
    macd_pane = chart.create_subchart(width=1000, height=200, sync=True) # sync=True: Ana grafikle x ekseni senkronize olur
    
    macd_calc = ta.macd(df['Close'])
    if macd_calc is not None and not macd_calc.empty:
        macd_line_data = pd.DataFrame({'time': df['time'], 'value': macd_calc.iloc[:, 0]})
        signal_line_data = pd.DataFrame({'time': df['time'], 'value': macd_calc.iloc[:, 2]})
        hist_data = pd.DataFrame({'time': df['time'], 'value': macd_calc.iloc[:, 1]})
        
        # MACD Histogramı için renk ataması (Yeşil/Kırmızı)
        hist_data['color'] = hist_data['value'].apply(lambda x: 'rgba(38, 166, 154, 0.8)' if x >= 0 else 'rgba(239, 83, 80, 0.8)')
        
        # Panele çizgileri ve histogramı ekle
        hist_series = macd_pane.create_histogram(name="MACD Hist")
        hist_series.set(hist_data)
        
        macd_series = macd_pane.create_line(color='#2962FF', width=2, name='MACD')
        signal_series = macd_pane.create_line(color='#FF6D00', width=2, name='Signal')
        
        macd_series.set(macd_line_data)
        signal_series.set(signal_line_data)

    # 5. Grafiği Streamlit Ekrana Bas
    chart.load()

elif df.empty:
    st.error("Veri çekilemedi. Lütfen sembolü kontrol edin.")
