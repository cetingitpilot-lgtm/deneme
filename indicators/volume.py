import plotly.graph_objects as go

BILGI = {"ad": "Hacim", "tip": "oscillator"}

def çiz(fig, df, row):
    renkler = ['#26a69a' if c >= o else '#ef5350' for c, o in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Hacim', marker_color=renkler), row=row, col=1)
