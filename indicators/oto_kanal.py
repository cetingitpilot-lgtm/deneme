import pandas as pd
import numpy as np
import plotly.graph_objects as go

class AutomatedChannel:
    NAME = "Oto Kanal" # Listede görünecek isim
    TYPE = "overlay"

    def __init__(self, length=100, deviation=2.0):
        self.length = length
        self.deviation = deviation
        self.show_markers = True

    def ciz(self, fig, df, x_axis, row=1):
        n = len(df)
        if n < self.length: return fig

        # --- Hesaplamalar ---
        subset_slice = slice(-self.length, None)
        x_indices = np.arange(n)
        x_subset = x_indices[subset_slice]
        y_subset = df['Close'].iloc[subset_slice].values

        # Lineer Regresyon (y = mx + b)
        slope, intercept = np.polyfit(x_subset, y_subset, 1)
        regression_line = slope * x_subset + intercept

        # Standart Sapma ve Kanal
        residuals = y_subset - regression_line
        std_dev = np.std(residuals)
        channel_width = self.deviation * std_dev

        top_line = regression_line + channel_width
        btm_line = regression_line - channel_width
        
        # Sinyaller
        curr_closes = df['Close'].iloc[subset_slice].values
        cross_up = (curr_closes > top_line) & (np.roll(curr_closes, 1) <= np.roll(top_line, 1))
        cross_up[0] = False 
        cross_down = (curr_closes < btm_line) & (np.roll(curr_closes, 1) >= np.roll(btm_line, 1))
        cross_down[0] = False

        x_dates = x_axis[subset_slice]

        # --- Çizim ---
        # Üst Çizgi
        fig.add_trace(go.Scatter(
            x=x_dates, y=top_line, mode='lines', 
            line=dict(color='#2962FF', width=2), 
            name='Kanal Üst', hoverinfo='skip'
        ), row=row, col=1)

        # Alt Çizgi
        fig.add_trace(go.Scatter(
            x=x_dates, y=btm_line, mode='lines', 
            line=dict(color='#2962FF', width=2), 
            name='Kanal Alt', fill='tonexty', 
            fillcolor='rgba(41, 98, 255, 0.1)', hoverinfo='skip'
        ), row=row, col=1)

        # Markerlar
        if self.show_markers:
            if np.any(cross_up):
                fig.add_trace(go.Scatter(
                    x=x_dates[cross_up], y=curr_closes[cross_up], 
                    mode='markers', marker=dict(symbol='triangle-up', size=10, color='green'), 
                    name='Yukarı Kırılım'
                ), row=row, col=1)
            if np.any(cross_down):
                fig.add_trace(go.Scatter(
                    x=x_dates[cross_down], y=curr_closes[cross_down], 
                    mode='markers', marker=dict(symbol='triangle-down', size=10, color='red'), 
                    name='Aşağı Kırılım'
                ), row=row, col=1)

        return fig

# --- KRİTİK BÖLÜM: MODÜL ENTEGRASYONU ---
# __init__.py dosyan modülü yüklüyor (import module).
# app.py dosyan ise 'module.ciz' ve 'module.NAME' arıyor.
# Bu yüzden sınıfı burada başlatıp özelliklerini modül seviyesine taşıyoruz.

_instance = AutomatedChannel(length=100, deviation=2.0)

NAME = _instance.NAME
TYPE = _instance.TYPE
ciz = _instance.ciz
