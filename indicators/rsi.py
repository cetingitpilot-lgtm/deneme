import pandas_ta as ta
import plotly.graph_objects as go

NAME = "RSI"
TYPE = "oscillator"

def ciz(fig, df, x_axis, row):
    df['RSI'] = ta.rsi(df['Close'], length=14)
    fig.add_trace(go.Scatter(x=x_axis, y=df['RSI'], name=NAME, 
                             line=dict(color='#7e57c2', width=2)), row=row, col=1)
    # Referans çizgileri
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=row, col=1, opacity=0.3)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=row, col=1, opacity=0.3)
    return fig
