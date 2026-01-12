import pandas as pd
import numpy as np
import plotly.graph_objects as go

# app.py'nin ve __init__.py'nin tanıması için gerekli anahtar değişkenler
NAME = "Oto Kanal"
TYPE = "overlay"

def ciz(fig, df, x_axis, row=1):
    """
    Otomatik Lineer Regresyon Kanalı Çizici
    """
    n = len(df)
    length = 100    # Kanalın bakacağı son bar sayısı
    deviation = 2.0  # Standart sapma çarpanı (Genişlik)

    if n < length:
        return fig

    # --- 1. Hesaplama Alanı ---
    subset_slice = slice(-length, None)
    x_indices = np.arange(n)
    x_subset = x_indices[subset_slice]
    y_subset = df['Close'].iloc[subset_slice].values

    # Lineer Regresyon (y = mx + b)
    slope, intercept = np.polyfit(x_subset, y_subset, 1)
    reg_line = slope * x_subset + intercept

    # Kanal Genişliği (Standart Sapma)
    std_dev = np.std(y_subset - reg_line)
    top_line = reg_line + (deviation * std_dev)
    btm_line = reg_line - (deviation * std_dev)

    # Plotly zaman ekseni (app.py'den gelen format)
    x_dates = x_axis[subset_slice]

    # --- 2. Çizim Alanı ---
    # Üst Çizgi
    fig.add_trace(go.Scatter(
        x=x_dates, y=top_line,
        mode='lines',
        line=dict(color='#2962FF', width=1.5),
        name='Kanal Üst',
        hoverinfo='skip'
    ), row=row, col=1)

    # Alt Çizgi ve Dolgu
    fig.add_trace(go.Scatter(
        x=x_dates, y=btm_line,
        mode='lines',
        line=dict(color='#2962FF', width=1.5),
        name='Kanal Alt',
        fill='tonexty',
        fillcolor='rgba(41, 98, 255, 0.1)',
        hoverinfo='skip'
    ), row=row, col=1)

    # Orta Trend Hattı
    fig.add_trace(go.Scatter(
        x=x_dates, y=reg_line,
        mode='lines',
        line=dict(color='rgba(255, 255, 255, 0.3)', width=1, dash='dot'),
        name='Trend',
        hoverinfo='none'
    ), row=row, col=1)

    return fig
