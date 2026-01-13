import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from indicators import MODULES

st.set_page_config(layout="wide")

symbol = st.text_input("Sembol", "AAPL")
df = yf.download(symbol, period="6mo", interval="1d")
df.dropna(inplace=True)

fig = go.Figure()

# === ANA FİYAT ===
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="Fiyat"
))

row = 1
for name, mod in MODULES.items():
    fig = mod.ciz(fig, df, df.index, row)
    row += 1

# === ORTAK HOVER & DİKEY ÇİZGİ ===
fig.update_layout(
    hovermode="x unified",
    spikedistance=-1,
    xaxis=dict(
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikedash="dot"
    )
)

st.plotly_chart(fig, use_container_width=True)
