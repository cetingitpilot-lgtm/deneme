import pandas_ta as ta
import plotly.graph_objects as go

NAME = "EMA 7"
TYPE = "overlay"

def ciz(fig, df, x_axis, row):
    df['EMA7'] = ta.ema(df['Close'], length=7)
    fig.add_trace(go.Scatter(x=x_axis, y=df['EMA7'], name=NAME, 
                             line=dict(color='yellow', width=1.5)), row=1, col=1)
    return fig
