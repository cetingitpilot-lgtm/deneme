import plotly.graph_objects as go

NAME = "Hacim"
TYPE = "oscillator"

def ciz(fig, df, x_axis, row):
    # Hacim barlarını renkli yapalım (Yükseliş yeşil, düşüş kırmızı)
    colors = ['green' if df['Close'][i] >= df['Open'][i] else 'red' for i in range(len(df))]
    fig.add_trace(go.Bar(x=x_axis, y=df['Volume'], name=NAME, marker_color=colors, opacity=0.5), row=row, col=1)
    return fig
