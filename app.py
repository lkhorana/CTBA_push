from dash import Dash, page_container, html
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)
server = app.server

# Navbar
navBar = dbc.NavbarSimple(
    color="dark",
    dark=True,
    fixed="top",
    brand_href="/",
  children=[
    dbc.NavLink("Home", href="/", active="exact"),
    "|",
    dbc.NavLink("Openings", href="/Openings", active="exact"),  
    "|",
    dbc.NavLink("Graph of Median Salaries", href="/Graph-of-Median-Salaries", active="exact"),  
],
    className="navbar"
)

# App layout
app.layout = html.Div([
    navBar,
    html.Div(page_container, style={"marginTop": "80px"})  # add top margin so content isn't hidden behind navbar
])

if __name__ == "__main__":
    app.run(debug=True)
