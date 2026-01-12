import pandas_ta as ta
import plotly.graph_objects as go

NAME = "EMA 14"
TYPE = "overlay"

def ciz(fig, df, x_axis, row):
    df['EMA14'] = ta.ema(df['Close'], length=14)
    fig.add_trace(go.Scatter(x=x_axis, y=df['EMA14'], name=NAME, 
                             line=dict(color='cyan', width=1.5)), row=1, col=1)
    return fig
