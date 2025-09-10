import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from fun_fact import get_unemployment_fact
from graph_fact import get_unemployment_graph

dash.register_page(__name__, path='/', name='Home')

# ---------------- Layout ----------------
layout = html.Div([

    # ---------------- Title ----------------
    html.Div([
        html.H2(
            "Graduate Program & Job Market Insight Dashboard",
            className="block block-title",
            style={"textAlign": "center"}
        )
    ], style={"marginBottom": "40px"}),

    # ---------------- Objective Section ----------------
    dbc.Col([
        html.H3(
            "Objective:",
            className="block block-subtitle",
            style={
                "fontWeight": "600",
                "fontSize": "24px",
                "marginBottom": "15px"
            }
        ),
        html.P(
            "This dashboard provides graduate students with insights into employment trends, skill demands, and career prospects. "
            "It helps students make informed decisions about post-graduation employment.",
            className="block block-hometext",
            style={
                "fontSize": "16px",
                "lineHeight": "1.6",
                "marginBottom": "0px"
            }
        )
    ], width=12, style={"marginBottom": "50px"}),

    # ---------------- Fun Fact + Graph Side by Side ----------------
    dbc.Row([

        # Fun Fact Column
        dbc.Col([
            html.H4(
                "Ever wonder what’s actually happening in the job market?",
                className="block block-subtitle"
            ),

            # Button wrapped in div with id for CSS
            html.Div(
                html.Button(
                    "Show Fun Fact",
                    id="fun-fact-button",   # used by callback
                    n_clicks=0,
                    className="btn"
                ),
                id="btn-popup",  # styled by your CSS
                style={"marginBottom": "20px"}
            ),

            # Fun fact text
            html.Div(
                id="fun-fact",
                style={
                    "opacity": "0",
                    "transition": "opacity 1s",
                    "marginBottom": "20px"
                }
            )
        ], width=6),

        # Graph Column
        dbc.Col([
            html.H4(
                "Unemployment Rate Over Time",
                className="block block-subtitle"
            ),
            dcc.Graph(
                id="unemployment-graph",
                style={"opacity": 0, "transition": "opacity 1s"}
            )
        ], width=6)

    ], style={"marginBottom": "50px"}),

], style={"padding": "30px"})


# ---------------- Callback: Fun Fact triggers and the Graph ----------------
@callback(
    Output("fun-fact", "children"),
    Output("fun-fact", "style"),
    Output("unemployment-graph", "figure"),
    Output("unemployment-graph", "style"),
    Input("fun-fact-button", "n_clicks")
)
def show_fun_fact(n_clicks):
    if n_clicks == 0:
        empty_style = {"opacity": 0}
        return "", empty_style, {}, {"opacity": 0}

    fact_text = get_unemployment_fact()

    # Fact + bullet points
    fact_content = html.Div([ #chatgpt helped ensure th notes will only ensure after you clik on the "show fact"
        html.P(fact_text, style={"fontWeight": "600", "marginBottom": "10px"}),
        html.Ul([
            html.Li("What does this employment fact mean?", style={"fontStyle": "italic"}),
            html.Li("The percent value shows how many people out of 100 are currently unemployed.", style={"fontStyle": "italic"}),
            html.Li("The lower the number, the better the employment situation is for you!", style={"fontStyle": "italic"}),
            html.Li("This dashboard helps you identify opportunities and trends to maximize your career prospects.", style={"fontStyle": "italic"})
        ])
    ]) #chatgpt helped set it up in a list format

    graph = get_unemployment_graph()
    fade_in_style = {"opacity": 1, "transition": "opacity 1s"}
    return fact_content, fade_in_style, graph, fade_in_style

