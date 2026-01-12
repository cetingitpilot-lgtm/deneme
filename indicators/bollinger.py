import pandas_ta as ta
import plotly.graph_objects as go

NAME = "Bollinger Bands"
TYPE = "overlay"

def ciz(fig, df, x_axis, row):
    # Bollinger bantlarını hesapla
    bb = ta.bbands(df['Close'], length=20, std=2)
    
    # Sütun isimleri bazen değişebildiği için ilk sütun Alt, orta sütun Orta, son sütun Üst banttır
    # bb.iloc[:, 0] -> Alt Bant, bb.iloc[:, 2] -> Üst Bant
    
    # Üst Bant (Şeffaf çizgi)
    fig.add_trace(go.Scatter(
        x=x_axis, y=bb.iloc[:, 2], 
        name="BB Üst", 
        line=dict(width=1, color='rgba(173, 216, 230, 0.4)')
    ), row=1, col=1)
    
    # Alt Bant ve Aradaki Dolgu
    fig.add_trace(go.Scatter(
        x=x_axis, y=bb.iloc[:, 0], 
        name="BB Alt", 
        fill='tonexty', # Bir önceki trace (Üst Bant) ile arasını doldurur
        fillcolor='rgba(173, 216, 230, 0.1)',
        line=dict(width=1, color='rgba(173, 216, 230, 0.4)')
    ), row=1, col=1)
    
    return fig
