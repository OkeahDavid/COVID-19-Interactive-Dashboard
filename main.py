import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from data_fetching import fetch_latest_data
from data_integrity_check import check_data_integrity


# Initialize the Dash application
app = dash.Dash(__name__)

# Fetch the latest COVID-19 data
data_url = 'https://covid19.who.int/WHO-COVID-19-global-data.csv'
default_data_path = 'WHO-COVID-19-global-data.csv' 

# Fetch the latest data or use the default dataset in case of an error
latest_data_file = fetch_latest_data(data_url, default_data_path)

# Load the CSV data into a DataFrame
covid_data = pd.read_csv(latest_data_file)

covid_data['Country'] = covid_data['Country'].fillna('Unknown')

# Perform data integrity checks
check_data_integrity(covid_data)

# Define the layout of the Dash application
app.layout = html.Div([
    html.H1("COVID-19 Dashboard"),
    html.Div([
        # Dropdown menu for selecting countries
        html.Div([
            html.Label('Select Country:'),
            dcc.Dropdown(
                id='country-dropdown',
                # Populate the dropdown options with unique countries from the dataset
                options=[{'label': country, 'value': country} for country in covid_data['Country'].unique()],
                value='United States of America',  # Default value
                multi=True  # Allow multiple selection
            ),
            # Date picker for selecting the date range
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=covid_data['Date_reported'].min(),
                end_date=covid_data['Date_reported'].max(),
                display_format='YYYY-MM-DD'
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),

        # Div for cumulative cases and deaths graphs
        html.Div([
            dcc.Graph(id='cumulative-cases-graph'),
            dcc.Graph(id='cumulative-deaths-graph'),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

        # Div for daily new cases and deaths graphs
        html.Div([
            dcc.Graph(id='daily-new-cases-graph'),
            dcc.Graph(id='daily-new-deaths-graph'),
        ], style={'width': '48%', 'display': 'inline-block'}),
    ])
])

# Callbacks to update the graphs based on user input
@app.callback(
    [Output('cumulative-cases-graph', 'figure'),
     Output('cumulative-deaths-graph', 'figure'),
     Output('daily-new-cases-graph', 'figure'),
     Output('daily-new-deaths-graph', 'figure')],
    [Input('country-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graphs(selected_countries, start_date, end_date):
    # Handle the case where a single country is selected
    if not isinstance(selected_countries, list):
        selected_countries = [selected_countries]

    # Filter the dataset based on the selected countries and date range
    filtered_df = covid_data[covid_data['Country'].isin(selected_countries) &
                             (covid_data['Date_reported'] >= start_date) &
                             (covid_data['Date_reported'] <= end_date)]

    # Create the figures for the four graphs
    cumulative_cases_fig = px.line(filtered_df, x='Date_reported', y='Cumulative_cases', color='Country',
                                   title='Cumulative COVID-19 Cases')
    cumulative_deaths_fig = px.line(filtered_df, x='Date_reported', y='Cumulative_deaths', color='Country',
                                    title='Cumulative COVID-19 Deaths')
    daily_new_cases_fig = px.bar(filtered_df, x='Date_reported', y='New_cases', color='Country',
                                 title='Daily New COVID-19 Cases')
    daily_new_deaths_fig = px.bar(filtered_df, x='Date_reported', y='New_deaths', color='Country',
                                  title='Daily New COVID-19 Deaths')

    return cumulative_cases_fig, cumulative_deaths_fig, daily_new_cases_fig, daily_new_deaths_fig

# Run the application
if __name__ == '__main__':
    app.run_server(debug=True)
