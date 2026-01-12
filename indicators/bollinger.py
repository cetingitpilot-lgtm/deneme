import pandas_ta as ta
import plotly.graph_objects as go

NAME = "Bollinger Bands"
TYPE = "overlay"

def ciz(fig, df, x_axis, row):
    bb = ta.bbands(df['Close'], length=20, std=2)
    # Üst Bant
    fig.add_trace(go.Scatter(x=x_axis, y=bb['BBU_20_2.0'], name="BB Üst", 
                             line=dict(width=1, color='rgba(173, 216, 230, 0.4)')), row=1, col=1)
    # Alt Bant ve Dolgu
    fig.add_trace(go.Scatter(x=x_axis, y=bb['BBL_20_2.0'], name="BB Alt", 
                             fill='tonexty', fillcolor='rgba(173, 216, 230, 0.1)',
                             line=dict(width=1, color='rgba(173, 216, 230, 0.4)')), row=1, col=1)
    return fig
