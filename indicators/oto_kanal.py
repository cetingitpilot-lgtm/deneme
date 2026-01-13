import plotly.graph_objects as go
import numpy as np

BILGI = {"ad": "Kanal", "tip": "overlay"}

def çiz(fig, df, row):
    y = df['Close'].values
    x = np.arange(len(y))
    s, i = np.polyfit(x, y, 1)
    kanal = s * x + i
    std = np.std(y - kanal)
    fig.add_trace(go.Scatter(x=df.index, y=kanal + std*2, name='K Üst', line=dict(dash='dot')), row=row, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=kanal - std*2, name='K Alt', line=dict(dash='dot')), row=row, col=1)
