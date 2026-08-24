import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import importlib
import indicators
import pandas as pd
from datetime import datetime, timedelta

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(layout="wide", page_title="Gemini Finansal Analiz")

# --- 1. YAN PANEL (SIDEBAR) BİLEŞENLERİ ---
st.sidebar.header("Grafik Ayarları")
symbol = st.sidebar.text_input("Sembol (Örn: BTC-USD veya THYAO.IS)", "BTC-USD")

timeframes = {
    "1 Dakika": "1m",
    "5 Dakika": "5m",
    "15 Dakika": "15m",
    "1 Saat": "1h",
    "1 Gün": "1d",
    "1 Hafta": "1wk"
}

secilen_tf_etiket = st.sidebar.selectbox(
    "Zaman Dilimi (Timeframe)", 
    options=list(timeframes.keys()), 
    index=2 # Varsayılan: 15 Dakika
)
interval_degeri = timeframes[secilen_tf_etiket]

# Tarih Aralığı Seçimi
bugun = datetime.now()
varsayilan_baslangic = bugun - timedelta(days=30) # Varsayılan olarak son 30 gün

tarih_araligi = st.sidebar.date_input(
    "Tarih Aralığı",
    value=(varsayilan_baslangic, bugun),
    max_value=bugun
)

# --- 2. VERİ ÇEKME FONKSİYONU ---
@st.cache_data(ttl=900)
def veri_cek(sembol, interval):
    # Zaman dilimine göre yfinance'in izin verdiği maksimum geçmişi ayarlıyoruz
    if interval == "1m":
        donem = "7d"
    elif interval in ["5m", "15m"]:
        donem = "60d"
    elif interval == "1h":
        donem = "730d"
    else:
        donem = "max"

    # Veriyi çek
    df = yf.download(sembol, period=donem, interval=interval)
    
    if df.empty:
        return df
        
    # MultiIndex düzeltmesi
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    
    # Sütun isimlerini standartlaştır (Open, High, Low, Close, Volume)
    df.columns = [str(c).capitalize() for c in df.columns]
    df = df.dropna()
    
    # Tüm sütunların float tipinde olduğundan emin ol
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    df = df.dropna()
    return df

# Veriyi çekiyoruz
df = veri_cek(symbol, interval_degeri)

# --- 3. VERİYİ TARİH ARALIĞINA GÖRE FİLTRELEME ---
if not df.empty and len(tarih_araligi) == 2:
    baslangic_tarihi, bitis_tarihi = tarih_araligi
    
    # yfinance indekslerindeki timezone bilgisini temizliyoruz ki filtreleme hata vermesin
    df.index = df.index.tz_localize(None) 
    
    # Bitiş tarihine 1 gün ekliyoruz ki seçilen son günün içindeki saatleri de kapsasın
    bitis_tarihi = bitis_tarihi + timedelta(days=1)
    
    # Veriyi maskeleyip daraltıyoruz
    mask = (df.index >= pd.to_datetime(baslangic_tarihi)) & (df.index <= pd.to_datetime(bitis_tarihi))
    df = df.loc[mask]

# Filtreleme sonrası Gapless (boşluksuz) formatı için indeksi string'e dönüştürüyoruz
if not df.empty:
    if interval_degeri in ["1d", "1wk"]:
        df.index = df.index.strftime('%Y-%m-%d')
    else:
        df.index = df.index.strftime('%Y-%m-%d %H:%M')

# En az 30 bar kontrolü (İndikatörlerin sağlıklı hesaplanabilmesi için)
if not df.empty and len(df) > 30:
    
    # --- DİNAMİK İNDİKATÖR YÜKLEME ---
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

    # Grafik Yapısı
    num_oscs = len(oscillator_mods)
    
    if num_oscs > 0:
        row_heights = [0.6] + [0.4 / num_oscs] * num_oscs
    else:
        row_heights = [1.0]

    fig = make_subplots(
        rows=1 + num_oscs, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.01, # Paneller arası boşluğu azalttık
        row_heights=row_heights
    )

    # --- 4. TRADINGVIEW STİLİ CANDLESTICK (FİYAT) ÇİZİMİ ---
    fig.add_trace(
        go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], 
            low=df['Low'], close=df['Close'], name="Fiyat",
            increasing_line_color='#26a69a', increasing_fillcolor='#26a69a', # TV Yükselen mum
            decreasing_line_color='#ef5350', decreasing_fillcolor='#ef5350'  # TV Düşen mum
        ), 
        row=1, col=1
    )

    # Overlay İndikatörleri Çiz
    for mod in overlay_mods:
        try:
            mod.çiz(fig, df, row=1)
        except Exception as e:
            st.sidebar.warning(f"{mod.BILGI['ad']} hata verdi: {str(e)}")

    # Oscillator İndikatörleri Çiz ve Etiketle
    for i, mod in enumerate(oscillator_mods, start=2):
        try:
            mod.çiz(fig, df, row=i)
            
            # Alt panellerdeki indikatör isimleri
            fig.add_annotation(
                text=f"<b>{mod.BILGI['ad']}</b>",
                xref=f"x{i} domain", yref=f"y{i} domain",
                x=0.01, y=0.95, showarrow=False,
                xanchor="left", yanchor="top", 
                font=dict(color="#d1d4dc", size=11), 
                bgcolor="rgba(19, 23, 34, 0.7)" 
            )
        except Exception as e:
            st.sidebar.warning(f"{mod.BILGI['ad']} hata verdi: {str(e)}")

    # --- 5. TRADINGVIEW GÖRÜNÜM VE EKSEN AYARLARI ---
    fig.update_layout(
        height=850,
        plot_bgcolor="#131722", # TV Arkaplan
        paper_bgcolor="#131722", 
        font=dict(color="#d1d4dc", family="Arial"), 
        hovermode="x unified",
        showlegend=False,
        dragmode="pan", # Kaydırma modu aktif
        margin=dict(l=20, r=60, t=30, b=20),
        xaxis_rangeslider_visible=False,
        hoverlabel=dict(
            bgcolor="#1e222d",
            font_size=13,
            font_family="Arial",
            bordercolor="#2a2e39"
        )
    )

    # X Ekseni (Zaman)
    fig.update_xaxes(
        type='category', # Gapless
        nticks=10, 
        showgrid=True, gridwidth=1, gridcolor='#2a2e39',
        showspikes=True, spikemode="across", spikesnap="cursor",
        spikedash="dash", spikecolor="#787b86", spikethickness=1,
        zeroline=False,
        fixedrange=False # Scroll ile X ekseninde yakınlaştırma/uzaklaştırmaya izin ver
    )
    
    # Ana Y Ekseni (Fiyat)
    fig.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor='#2a2e39',
        zeroline=False,
        side="right", # Fiyat sağda
        fixedrange=False # Eksen üzerinden tutularak mum boyutu ayarlamaya izin ver
    )
    
    # Alt Panellerin Y Eksenleri
    for i in range(2, num_oscs + 2):
        fig.layout[f"yaxis{i}"].update(
            showgrid=True, gridwidth=1, gridcolor='#2a2e39',
            zeroline=False, side="right", fixedrange=False
        )

    # Ana fiyat paneli başlığı
    fig.add_annotation(
        text=f"<b>{symbol} • {secilen_tf_etiket.upper()}</b>",
        xref="paper", yref="paper",
        x=0.01, y=0.99, showarrow=False,
        xanchor="left", yanchor="top", 
        font=dict(color="#d1d4dc", size=14),
        bgcolor="rgba(19, 23, 34, 0.8)"
    )

    # --- 6. PLOTLY KONTROL BARI AYARLARI ---
    config = {
        'scrollZoom': True, # Fare tekerleğiyle yakınlaştırma aktif
        'displayModeBar': True,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'autoScale2d'], # Gereksiz araçları gizle
        'modeBarButtonsToAdd': ['drawline', 'drawrect'], # Çizim araçları eklendi
        'displaylogo': False
    }
    
    st.plotly_chart(fig, use_container_width=True, config=config)

# --- 7. HATA MESAJLARI ---
elif df.empty:
    st.error("Veri çekilemedi. Lütfen sembolü kontrol edin veya seçtiğiniz tarih aralığında piyasanın açık olduğundan emin olun.")
else:
    st.warning(f"Seçili sembol veya tarih aralığı için yeterli veri yok. ({len(df)} bar bulundu, indikatörler için en az 30 bar gereklidir.)")
