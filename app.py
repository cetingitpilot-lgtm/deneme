import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import indicators

st.set_page_config(layout="wide")

st.sidebar.title("📊 Teknik Analiz")

symbol = st.sidebar.text_input("Hisse / Kripto", "AAPL")
period = st.sidebar.selectbox("Zaman Aralığı", ["1mo", "3mo", "6mo", "1y", "2y"])
interval = st.sidebar.selectbox("Periyot", ["1d", "1h", "1wk"])

indicator_names = list(indicators.MODULLER.keys())
selected = st.sidebar.multiselect(
    "İndikatörler",
    indicator_names,
    default=["EMA 7", "RSI"]
)

df = yf.download(symbol, period=period, interval=interval)

if df.empty:
    st.error("Veri alınamadı")
    st.stop()

osc_count = sum(
    1 for i in selected if indicators.MODULLER[i].TYPE == "oscillator"
)

rows = 1 + osc_count

fig = make_subplots(
    rows=rows,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.5] + [0.5 / osc_count] * osc_count if osc_count > 0 else [1]
)

# === ANA FİYAT GRAFİĞİ ===
fig.add_candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="Fiyat",
    row=1,
    col=1
)

current_row = 2

for name in selected:
    mod = indicators.MODULLER[name]

    if mod.TYPE == "overlay":
        fig = mod.ciz(fig, df, df.index, 1)

    else:
        fig = mod.ciz(fig, df, df.index, current_row)

        # ❌ Oscillator çizgileri kapat
        fig.update_yaxes(
            showline=False,
            zeroline=False,
            row=current_row,
            col=1
        )

        current_row += 1

# === TÜM GRAFİKLERDE ORTAK DİKEY ÇİZGİ ===
fig.update_layout(
    hovermode="x unified",
    spikedistance=-1
)

fig.update_xaxes(
    showspikes=True,
    spikemode="across",
    spikesnap="cursor",
    spikecolor="gray",
    spikethickness=1
)

# ❌ Mouse ile gezen hover kapalı
fig.update_traces(hoverinfo="skip")

# === SABİT BİLGİ PANELİ ===
fig.add_annotation(
    xref="paper",
    yref="paper",
    x=0.01,
    y=0.98,
    showarrow=False,
    align="left",
    bgcolor="rgba(0,0,0,0.75)",
    font=dict(size=11, color="white"),
    text="Hover için mum üzerinde gez"
)

fig.update_layout(
    height=900,
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(fig, use_container_width=True)
