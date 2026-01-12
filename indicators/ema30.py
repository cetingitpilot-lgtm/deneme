import pandas_ta as ta
import plotly.graph_objects as go

NAME = "EMA 30"
TYPE = "overlay"

def ciz(fig, df, x_axis, row):
    df['EMA30'] = ta.ema(df['Close'], length=30)
    fig.add_trace(go.Scatter(x=x_axis, y=df['EMA30'], name=NAME, 
                             line=dict(color='magenta', width=1.5)), row=1, col=1)
    return fig
