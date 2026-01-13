import pandas_ta as ta
import plotly.graph_objects as go

def ciz(fig, df, x, row):
    bb = ta.bbands(df["Close"], length=20)

    lower = bb.iloc[:, 0]
    middle = bb.iloc[:, 1]
    upper = bb.iloc[:, 2]

    fig.add_trace(go.Scatter(x=x, y=upper, name="BB Upper", line=dict(color="gray")))
    fig.add_trace(go.Scatter(x=x, y=middle, name="BB Middle", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=x, y=lower, name="BB Lower", line=dict(color="gray")))

    return fig
