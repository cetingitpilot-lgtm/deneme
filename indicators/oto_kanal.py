import pandas as pd
import numpy as np
import plotly.graph_objects as go

# app.py'nin beklediği değişkenler
NAME = "Oto Kanal"
TYPE = "overlay"

def ciz(fig, df, x_axis, row=1):
    # Fonksiyonun içinde sınıfı başlatıp çalıştırıyoruz
    # Bu yöntem importlib hatalarını minimize eder
    obj = AutomatedChannelLogic()
    return obj.ciz_islem(fig, df, x_axis, row)

class AutomatedChannelLogic:
    def __init__(self, length=100, deviation=2.0):
        self.length = length
        self.deviation = deviation

    def ciz_islem(self, fig, df, x_axis, row):
        n = len(df)
        if n < self.length: return fig

        # (Buraya daha önce verdiğim lineer regresyon hesaplamalarını koy)
        subset_slice = slice(-self.length, None)
        x_indices = np.arange(n)
        x_subset = x_indices[subset_slice]
        y_subset = df['Close'].iloc[subset_slice].values

        slope, intercept = np.polyfit(x_subset, y_subset, 1)
        reg_line = slope * x_subset + intercept
        
        std_dev = np.std(y_subset - reg_line)
        top = reg_line + (self.deviation * std_dev)
        btm = reg_line - (self.deviation * std_dev)

        x_dates = x_axis[subset_slice]

        fig.add_trace(go.Scatter(x=x_dates, y=top, line=dict(color='#2962FF', width=1), name='Kanal Üst'), row=row, col=1)
        fig.add_trace(go.Scatter(x=x_dates, y=btm, line=dict(color='#2962FF', width=1), name='Kanal Alt', fill='tonexty', fillcolor='rgba(41, 98, 255, 0.1)'), row=row, col=1)
        
        return fig
