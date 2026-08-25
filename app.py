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
    
    # 1. Veriyi çekiyoruz
    df = yf.download(sembol, period=donem, interval=iv)
    
    # Eğer doğrudan boş gelirse hemen dön
    if df.empty: return pd.DataFrame()
    
    # 2. MultiIndex (Çoklu Sütun) yapısını tek seviyeye indir (yfinance'ın yeni sürümü bazen böyle döner)
    if isinstance(df.columns, pd.MultiIndex): 
        df.columns = [col[0] for col in df.columns]
    
    # 3. İndeksi sıfırla (Böylece Datetime indeksi normal bir sütun olur)
    df = df.reset_index()
    
    # 4. Sütun isimlerini zorla küçük harfe çevir (Open -> open)
    df.columns = [str(c).lower() for c in df.columns]
    
    # 5. Tarih sütununun ismini 'time' olarak ayarla (İlk sütun her zaman tarihtir)
    df.rename(columns={df.columns[0]: 'time'}, inplace=True)
    
    # 6. Güvenlik Kontrolü: İlgili OHLC sütunları gerçekten var mı?
    gerekli_sutunlar = ['open', 'high', 'low', 'close']
    if not all(col in df.columns for col in gerekli_sutunlar):
        # Sütunlar beklenen formatta değilse boş döndür (Hata mesajını tetikler)
        return pd.DataFrame()
        
    # 7. Sayısal veri dönüşümü (Float)
    for col in gerekli_sutunlar + ['volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)
            
    # Eksik verili (NaN) satırları sil
    df = df.dropna(subset=['open', 'high', 'low', 'close'])
    
    # 8. Zaman Formatını Düzenleme (JavaScript uyumluluğu için)
    # yfinance'tan gelen tarih verisini standart pandas datetime'a çeviriyoruz
    df['time'] = pd.to_datetime(df['time'], utc=True)
    
    # Eğer saat dilimi (timezone) bilgisi varsa kaldır
    df['time'] = df['time'].dt.tz_localize(None)
    
    # Grafik zaman dilimine göre (interval) string formatına çevir
    if iv == '1d':
        df['time'] = df['time'].dt.strftime('%Y-%m-%d')
    else:
        df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return df

# Veriyi değişkene ata
df = veri_cek(symbol, interval)

# --- VERİ İŞLEME VE GRAFİK ÇİZİMİ ---
if not df.empty and len(df) > 30:
    st.markdown(f"### {symbol} • {secilen_tf_etiket.upper()}")
    
    # İndikatör Hesaplamaları
    bb = ta.bbands(df['close'], length=20, std=2)
    macd = ta.macd(df['close'])
    stoch = ta.stochrsi(df['close'])
    
    # Kütüphane Yapısı
    chart = StreamlitChart(width=1100, height=800, inner_width=1, inner_height=0.5)
    macd_pane = chart.create_subchart(width=1, height=0.25, sync=True)
    stoch_pane = chart.create_subchart(width=1, height=0.25, sync=True)

    # Tema ve Renkler
    chart.layout(background_color=bg_color, text_color=text_color, font_size=12, font_family="Arial")
    chart.grid(vert_enabled=True, horz_enabled=True, color=grid_color)
    chart.crosshair(mode='normal', vert_color=crosshair_color, vert_style='dashed', horz_color=crosshair_color, horz_style='dashed')
    chart.time_scale(right_offset=10, min_bar_spacing=2)

    macd_pane.layout(background_color=bg_color, text_color=text_color, font_size=12, font_family="Arial")
    macd_pane.grid(vert_enabled=True, horz_enabled=True, color=grid_color)
    
    stoch_pane.layout(background_color=bg_color, text_color=text_color, font_size=12, font_family="Arial")
    stoch_pane.grid(vert_enabled=True, horz_enabled=True, color=grid_color)

    # --- VERİ BAĞLAMA (.to_dict('records') KULLANIMI) ---
    
    # 1. Ana Fiyat (Dict listesine çevrildi)
    fiyat_verisi = df[['time', 'open', 'high', 'low', 'close', 'volume']].to_dict('records')
    chart.set(fiyat_verisi)

    # 2. Bollinger Bantları
    if bb is not None and not bb.empty:
        line_bbu = chart.create_line(color='rgba(136, 136, 136, 0.7)', width=1)
        line_bbl = chart.create_line(color='rgba(136, 136, 136, 0.7)', width=1)
        
        df_bbu = pd.DataFrame({'time': df['time'], 'value': bb.iloc[:, 2].astype(float)}).dropna()
        df_bbl = pd.DataFrame({'time': df['time'], 'value': bb.iloc[:, 0].astype(float)}).dropna()
        
        line_bbu.set(df_bbu.to_dict('records'))
        line_bbl.set(df_bbl.to_dict('records'))

    # 3. MACD
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
            
        hist_series.set(df_hist.to_dict('records'))
        macd_series.set(df_macd_line.to_dict('records'))
        signal_series.set(df_signal_line.to_dict('records'))

    # 4. STOCH RSI
    if stoch is not None and not stoch.empty:
        stoch_k = stoch_pane.create_line(color='#2962FF', width=2)
        stoch_d = stoch_pane.create_line(color='#FF6D00', width=2)
        
        df_stoch_k = pd.DataFrame({'time': df['time'], 'value': stoch.iloc[:, 0].astype(float)}).dropna()
        df_stoch_d = pd.DataFrame({'time': df['time'], 'value': stoch.iloc[:, 1].astype(float)}).dropna()
        
        stoch_k.set(df_stoch_k.to_dict('records'))
        stoch_d.set(df_stoch_d.to_dict('records'))

    # Grafiği Yükle
    chart.load()

elif df.empty:
    st.error("Veri çekilemedi. Bu durum şunlardan kaynaklanabilir:\n\n1. Sembol yanlış olabilir (BTC-USD yazmayı unutmayın).\n2. Yfinance servisi geçici olarak yanıt vermiyor olabilir.\n3. İnternet bağlantınız kısıtlı olabilir.")
else:
    st.warning("Yeterli veri bulunamadı. İndikatör hesaplamaları için en az 30 bar veriye ihtiyaç vardır.")
