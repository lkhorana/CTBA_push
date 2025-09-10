import dash
from dash import register_page, dcc, callback, html, Input, Output  
import requests
import pandas as pd
import plotly.express as px


# Registering page
register_page(__name__, path='/Openings', name='Openings')

url = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
key = '62a39a9417d948298af08401d3fba818'

# Industry dictionary 
industry = {
    "Total nonfarm": "JTS000000000000000JOR",
    "Total private": "JTS100000000000000JOR",
    "Mining and logging": "JTS110099000000000JOR",
    "Construction": "JTS230000000000000JOR",
    "Manufacturing": "JTS300000000000000JOR",
    "Durable goods manufacturing": "JTS320000000000000JOR",
    "Nondurable goods manufacturing": "JTS340000000000000JOR",
    "Trade, transportation, and utilities": "JTS400000000000000JOR",
    "Wholesale trade": "JTS420000000000000JOR",
    "Retail trade": "JTS440000000000000JOR",
    "Transportation, warehousing, and utilities": "JTS480099000000000JOR",
    "Information": "JTS510000000000000JOR",
    "Financial activities": "JTS510099000000000JOR",
    "Finance and insurance": "JTS520000000000000JOR",
    "Real estate and rental and leasing": "JTS530000000000000JOR",
    "Professional and business services": "JTS540099000000000JOR",
    "Private education and health services": "JTS600000000000000JOR",
    "Private educational services": "JTS610000000000000JOR",
    "Health care and social assistance": "JTS620000000000000JOR",
    "Leisure and hospitality": "JTS700000000000000JOR",
    "Arts, entertainment, and recreation": "JTS710000000000000JOR",
    "Accommodation and food services": "JTS720000000000000JOR",
    "Other services": "JTS810000000000000JOR",
    "Government": "JTS900000000000000JOR",
    "Federal": "JTS910000000000000JOR",
    "State and local": "JTS920000000000000JOR",
    "State and local government education": "JTS923000000000000JOR",
    "State and local government, excluding education": "JTS929000000000000JOR"
}


###NOTE: Ai assistance was used to help refine code for all sections below here ####



# Fetching data from BLS API with error handling
def fetch_bls_data(series_id, startyear="2015", endyear="2024"):
    if not series_id:
        raise ValueError("Series ID is missing.")

    payload = {
        "seriesid": [series_id],
        "startyear": startyear,
        "endyear": endyear,
        "registrationKey": key
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)  
        resp.raise_for_status()  
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to connect to BLS API: {e}")

    try:
        data = resp.json()
    except ValueError:
        raise ValueError("Invalid JSON response from BLS API.")

    # Check if expected keys exist
    if 'Results' not in data or 'series' not in data['Results']:
        raise KeyError("Unexpected API response structure.")

    series_data = data['Results']['series'][0].get('data', [])
    if not series_data:
        raise ValueError("No data returned for the selected series.")

    rows = []
    for item in series_data:
        try:
            rows.append({
                "year": item["year"],
                "period": item["periodName"],
                "value": float(item["value"])
            })
        except (KeyError, ValueError):
            continue  # Skip invalid rows

    if not rows:
        raise ValueError("No valid numeric data available for this series.")

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["year"] + " " + df["period"], errors='coerce')
    df = df.dropna(subset=["date"]).sort_values("date")
    return df[["date", "value"]]


# Dash layout 
layout = html.Div([
    html.H1("Job Openings Time Series"),
    html.H2("Data pulled from JOLTS, filtered by industry"),
    html.Label("Choose Industry:"),
    html.Div(dcc.Dropdown(
        id="industry-dropdown",
        options=[{"label": k, "value": v} for k, v in industry.items()],
        value="JTS000000000000000JOR",  # Default = Total Nonfarm
        clearable=False
    ), className= "dropdown"),
    dcc.Graph(id="forecast-graph")
])

# Callback with error handling
@callback(
    Output("forecast-graph", "figure"),
    Input("industry-dropdown", "value")
)
def update_forecast(series_id):
    try:
        df = fetch_bls_data(series_id)
        df.set_index("date", inplace=True)

        
        fig = px.line(df, x=df.index, y="value", title="Job Openings (Historical)", labels={"value": "Percent Job Openings", "index": "Date"})
    except Exception as e:
        # Display error message in plot
        fig = px.line(title=f"Error: {e}")
        fig.update_layout(xaxis={"visible": False}, yaxis={"visible": False})
    return fig
