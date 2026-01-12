import pandas as pd
import numpy as np
import plotly.graph_objects as go

# app.py'nin ve __init__.py'nin tanıması için gerekli değişkenler
NAME = "Oto Kanal"
TYPE = "overlay"

def ciz(fig, df, x_axis, row=1):
    """
    Bu fonksiyon app.py içindeki dongu tarafından çağrılır.
    """
    n = len(df)
    length = 100  # Geriye dönük kaç bar baz alınacak
    deviation = 2.0 # Kanal genişliği çarpanı

    if n < length:
        return fig

    # --- 1. Lineer Regresyon Hesaplama ---
    subset_slice = slice(-length, None)
    x_indices = np.arange(n)
    x_subset = x_indices[subset_slice]
    y_subset = df['Close'].iloc[subset_slice].values

    # Geçersiz veri kontrolü (NaN vs)
    if np.any(np.isnan(y_subset)):
        y_subset = np.nan_to_num(y_subset, nan=np.nanmean(y_subset))

    # Eğim ve Kesişim Bulma
    slope, intercept = np.polyfit(x_subset, y_subset, 1)
    reg_line = slope * x_subset + intercept

    # --- 2. Kanal Genişliği (Standart Sapma) ---
    std_dev = np.std(y_subset - reg_line)
    top_line = reg_line + (deviation * std_dev)
    btm_line = reg_line - (deviation * std_dev)

    # Plotly için zaman ekseni
    x_dates = x_axis[subset_slice]

    # --- 3. Grafiğe Ekleme ---
    # Üst Sınır
    fig.add_trace(go.Scatter(
        x=x_dates, y=top_line,
        mode='lines',
        line=dict(color='#2962FF', width=1.5),
        name='Kanal Üst',
        hoverinfo='skip'
    ), row=row, col=1)

    # Alt Sınır ve Dolgu
    fig.add_trace(go.Scatter(
        x=x_dates, y=btm_line,
        mode='lines',
        line=dict(color='#2962FF', width=1.5),
        name='Kanal Alt',
        fill='tonexty',
        fillcolor='rgba(41, 98, 255, 0.1)',
        hoverinfo='skip'
    ), row=row, col=1)

    # Orta Hat (Trend)
    fig.add_trace(go.Scatter(
        x=x_dates, y=reg_line,
        mode='lines',
        line=dict(color='rgba(255, 255, 255, 0.2)', width=1, dash='dot'),
        name='Trend Hattı',
        hoverinfo='none'
    ), row=row, col=1)

    return fig
