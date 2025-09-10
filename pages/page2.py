# AI ASSISTANCE LOG
# -----------------
# Used Gemini to help structure the initial Dash application layout and the
# data preparation pipeline. Gemini also assisted with debugging data-related
# errors (e.g., incorrect column names, file paths) and provided code snippets
# for implementing new features. Specific complex tasks included developing the
# function to standardize different pay periods (hourly, monthly) into an annual
# salary, implementing the dynamic data aggregation within the callback, and
# creating the pandas logic to identify the highest-paid job title for each state. Used Gemini to refine and convert the code from a single page app to a page in a multipage app.
# The final code was reviewed and edited for correctness.


import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, register_page
import os
from pathlib import Path

# --- Register this page with Dash ---
# This line tells our main app.py file that this script is a page.
# The 'path' determines the URL, and 'name' is for the navigation link.
register_page(__name__, path='/Graph-of-Median-Salaries', name='Graph of Median Salaries')

# --- Data Loading and Preparation ---
# This big function does all the heavy lifting of getting our data ready.
# It's called only once when the app starts to make things faster.
def load_and_prepare_data():
    """
    Loads, merges, and prepares a clean DataFrame of all USA job listings.
    """
    print("Starting data preparation for map page...")
    
    # We'll wrap our file loading in a try/except block. That way, if the CSV files
    # are missing, the app won't crash; it will just show an error message.
    try:
        # We use pathlib to build the file path. This is a good habit because it
        # makes the script work on any operating system (Windows, Mac, etc.).
        data_folder = Path(__file__).resolve().parent.parent / "data"
        df_main = pd.read_csv(os.path.join(data_folder, 'glassdoor.csv'))
        df_salaries = pd.read_csv(os.path.join(data_folder, 'glassdoor_salary_salaries.csv'))
        print("Successfully read both CSV files.")
    except FileNotFoundError as e:
        print(f"Error: A source CSV file was not found. {e}")
        return pd.DataFrame()

    # Here, we join our two data files into one big table. We're using a 'left' merge
    # to make sure we keep all the jobs from the main file.
    df_merged = pd.merge(df_main, df_salaries, left_on='salary.salaries', right_on='id', how='left')
    
    # We've got over 150 columns, but we only need a few. Let's define the ones
    # we care about and give them simple, friendly names.
    required_columns = {
        'map.location': 'location',
        'header.jobTitle': 'job_title',
        'overview.industry': 'industry',
        'salary.salaries.val.salaryPercentileMap.payPercentile50': 'median_salary',
        'salary.salaries.val.payPeriod': 'pay_period'
    }
    # This is a quick check to make sure all the columns we need actually exist.
    if not all(col in df_merged.columns for col in required_columns.keys()):
        print("Error: Required columns not found in the merged data.")
        return pd.DataFrame()

    # Now we create our smaller, cleaner DataFrame and get rid of any rows
    # that are missing the essential info we need.
    df_clean = df_merged[list(required_columns.keys())].copy()
    df_clean.rename(columns=required_columns, inplace=True)
    df_clean.dropna(subset=['location', 'median_salary', 'job_title', 'pay_period', 'industry'], inplace=True)
    
    # AI assistance was used for the salary standardization logic (see log at top).
    # This little helper function checks if a salary is hourly or monthly and
    # converts it to an annual figure. This is super important for accurate data.
    def standardize_salary(row):
        salary = row['median_salary']
        period = row['pay_period']
        if period == 'HOURLY': return salary * 2080 # 40 hours/week * 52 weeks
        if period == 'MONTHLY': return salary * 12
        return salary # If it's not hourly or monthly, we assume it's already annual.

    # We apply our function to every row in the salary column.
    df_clean['median_salary'] = df_clean.apply(standardize_salary, axis=1)
    
    # This uses a regular expression to pull out the two-letter state code from
    # the location string (e.g., "New York, NY" becomes "NY").
    df_clean['state'] = df_clean['location'].str.extract(r',\s*([A-Z]{2})$')
    # Finally, we drop any rows that aren't in the US or have a bad industry value.
    df_usa = df_clean.dropna(subset=['state'])
    df_usa = df_usa[df_usa['industry'] != '-1']
    
    print(f"Data preparation complete. Found {len(df_usa)} valid data jobs in the USA.")
    # The function returns the final, clean dataset that our app will use.
    return df_usa

# This line runs our big data prep function and stores the result in 'df'.
df = load_and_prepare_data()

# We get a sorted, unique list of industries to use as the options in our dropdown menu.
if not df.empty:
    industry_options = [{'label': 'All Industries', 'value': 'All Industries'}] + \
                       [{'label': industry, 'value': industry} for industry in sorted(df['industry'].unique())]
else:
    industry_options = []

# --- Page Layout ---
# This 'layout' variable defines the entire visual structure of this page.
# Dash automatically finds this variable when it loads the page.
layout = html.Div(
    children=[
        # This is the main title for our page.
        html.H1("Interactive Salary Map"),
        
        # This Div holds our two summary cards side-by-side.
        html.Div([
            # The first card shows the max salary. Its content will be updated by our callback.
            html.Div([
                html.H4("Overall Max Salary", style={'textAlign': 'center', "color": "#333333"}),
                html.P(id='max-salary-card', style={'textAlign': 'center', 'fontSize': 24, 'fontWeight': 'bold', "color": "#333333"})
            ], style={'width': '48%', 'display': 'inline-block', 'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '5px'}),
            
            # The second card shows the most common job title.
            html.Div([
                html.H4("Overall Most Common Job", style={'textAlign': 'center', "color": "#333333"}),
                html.P(id='common-job-card', style={'textAlign': 'center', 'fontSize': 24, 'fontWeight': 'bold', "color": "#333333"})
            ], style={'width': '48%', 'display': 'inline-block', 'float': 'right', 'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '5px'})
        ], style={'padding': '20px 0'}),

        # This Div holds our two filter controls: the dropdown and the search box.
        html.Div([
            # The dropdown menu for filtering by industry.
            html.Div([
                html.Label("Select an Industry:", style={"color": "#ffffff"}),
                dcc.Dropdown(id='industry-dropdown', options=industry_options, value='All Industries', clearable=False)
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            # The text input box for searching job titles.
            html.Div([
                html.Label("Search for a Job Title:", style={"color": "#ffffff"}),
                dcc.Input(
                    id='job-title-search',
                    type='text',
                    placeholder='e.g., Data Engineer, Data Scientist...',
                    debounce=True, # This is a nice feature that waits for you to stop typing.
                    style={'width': '100%'}
                )
            ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
        ], style={'padding': '20px 0'}),
        
        # This is the placeholder for our map. The callback will fill this in.
        dcc.Graph(id='choropleth-map-salaries'),
    ]
)

# --- Callback to Update Map AND Cards ---
# This is the "brain" of our app. It connects the user inputs (filters) to the
# outputs (the map and cards). It re-runs every time a filter changes.
@dash.callback(
    Output('choropleth-map-salaries', 'figure'),
    Output('max-salary-card', 'children'),
    Output('common-job-card', 'children'),
    Input('industry-dropdown', 'value'),
    Input('job-title-search', 'value')
)
def update_map_and_cards(selected_industry, search_term):
    #Used AI Assistance to create this function. 
    #If our data failed to load, just return empty components.
    if df.empty:
        return px.choropleth(scope="usa"), "N/A", "N/A"

    # We start with a full copy of the data and then apply our filters.
    filtered_df = df.copy()

    # Apply the job title search if the user has typed anything.
    if search_term and search_term.strip() != '':
        filtered_df = filtered_df[filtered_df['job_title'].str.contains(search_term, case=False)]
        title_search = f" containing '{search_term}'"
    else:
        title_search = ""

    # Apply the industry filter.
    if selected_industry != 'All Industries':
        filtered_df = filtered_df[filtered_df['industry'] == selected_industry]
        title_industry = selected_industry
    else:
        title_industry = "All Industries"

    # If our filters result in no data, show a friendly message.
    if filtered_df.empty:
        fig = px.choropleth(scope="usa", title=f"No Data Jobs Found for the Selected Filters")
        fig.update_layout(paper_bgcolor='#FFFFFF', font_color='#333333', title_x=0.5)
        return fig, "N/A", "N/A"
        
    # Calculate the summary stats for the two cards from our filtered data.
    overall_max_salary = f"${filtered_df['median_salary'].max():,.0f}"
    overall_common_job = filtered_df['job_title'].mode().iloc[0]

    # AI assistance was used for the dynamic data aggregation logic (see log at top).
    # Now, we aggregate the filtered data to get one summary row per state for the map.
    df_state_agg = filtered_df.groupby('state').agg(
        median_salary=('median_salary', 'median'),
        max_salary=('median_salary', 'max'),
        common_job=('job_title', lambda x: x.mode().iloc[0] if not x.mode().empty else "N/A")
    ).reset_index()

    # AI assistance was used for this pandas logic (see log at top).
    # This is a clever pandas trick to find the actual job title that had the max salary.
    highest_paid_jobs = filtered_df.loc[filtered_df.groupby('state')['median_salary'].idxmax()]
    highest_paid_jobs = highest_paid_jobs[['state', 'job_title']].rename(columns={'job_title': 'highest_paid_job'})
    
    # We merge our main stats with the highest-paid job titles.
    df_final_agg = pd.merge(df_state_agg, highest_paid_jobs, on='state')

    # Finally, we create the choropleth map with our prepared data.
    fig = px.choropleth(
        df_final_agg, 
        locations='state', 
        locationmode="USA-states", 
        color='median_salary',
        custom_data=['common_job', 'max_salary', 'highest_paid_job'], # This data is for the tooltip.
        color_continuous_scale="Blues",
        scope="usa",
        labels={'median_salary': 'Median Salary (USD)'},
        title=f"Median Salaries for Data Jobs{title_search} in {title_industry}"
    )
    
    # This custom template makes our hover-over tooltips look nice and clean.
    fig.update_traces(
        hovertemplate=(
            "<b>%{location}</b><br><br>"
            "Median Salary: %{z:$,.0f}<br>"
            "Max Salary: %{customdata[1]:$,.0f}<br>"
            "Highest Paid Job: %{customdata[2]}<br>"
            "Most Common Job: %{customdata[0]}"
            "<extra></extra>" # This little tag hides an extra box that Plotly sometimes shows.
        )
    )
    
    # Here we set the colors and other styling for the map.
    fig.update_layout(
        paper_bgcolor='#2d2d30',
        font_color='#ffffff',
        title_x=0.5,
        margin=dict(l=10, r=10, t=50, b=10),
        geo=dict(bgcolor='rgba(0,0,0,0)')
    )
    
    # The function returns all the components that need to be updated on the page.
    return fig, overall_max_salary, overall_common_job
