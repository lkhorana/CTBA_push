import plotly.express as px
from fun_fact import get_unemployment_data  # reuse the function

def get_unemployment_graph():
    months, values = get_unemployment_data()
    if not months:
        # empty figure if API fails
        fig = px.line(title="You've maxed out the API request quota, please try again another time!")
        return fig

    # Create a simple line chart with markers and gradient fill
    fig = px.line(
        x=months,
        y=values,
        labels={"x": "Month", "y": "Unemployment Rate (%)"},
        title="US Unemployment Rate Over Time",
        markers=True
    )

    # Update layout for- to avoid the bland look
    fig.update_layout(
        title=dict(text="US Unemployment Rate Over Time", font=dict(size=22, color="#222"), x=0.5),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#f5f5f5",
        xaxis=dict(
            showgrid=True,
            gridcolor="#eaeaea",
            tickangle=-45,
            tickfont=dict(size=11, color="#555"),
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#eaeaea",
            tickfont=dict(size=11, color="#555"),
            zeroline=False
        ),
        margin=dict(l=60, r=40, t=100, b=60),
        hovermode="x unified"
    )

    return fig
