import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from data_fetching import fetch_latest_data

# Initialize the Dash application
app = dash.Dash(__name__)

# Update the data URL to use Our World in Data's COVID-19 dataset
data_url = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
default_data_path = 'owid-covid-data.csv'

try:
    # Fetch the latest data
    latest_data_file = fetch_latest_data(data_url, default_data_path)
    
    # Load and process the CSV data
    covid_data = pd.read_csv(latest_data_file)
    
    # Rename columns to match our application's expectations
    covid_data = covid_data.rename(columns={
        'location': 'Country',
        'date': 'Date_reported',
        'total_cases': 'Cumulative_cases',
        'total_deaths': 'Cumulative_deaths',
        'new_cases': 'New_cases',
        'new_deaths': 'New_deaths'
    })

    # Fill any missing values
    covid_data['Country'] = covid_data['Country'].fillna('Unknown')
    
    # Convert date column to datetime
    covid_data['Date_reported'] = pd.to_datetime(covid_data['Date_reported'])

    # Define the layout
    app.layout = html.Div([
        html.H1("COVID-19 Dashboard"),
        html.Div([
            html.Div([
                html.Label('Select Country:'),
                dcc.Dropdown(
                    id='country-dropdown',
                    options=[{'label': country, 'value': country} 
                            for country in sorted(covid_data['Country'].unique())],
                    value='United States',
                    multi=True
                ),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date=covid_data['Date_reported'].min(),
                    end_date=covid_data['Date_reported'].max(),
                    display_format='YYYY-MM-DD'
                ),
            ], style={'width': '48%', 'display': 'inline-block'}),

            html.Div([
                dcc.Graph(id='cumulative-cases-graph'),
                dcc.Graph(id='cumulative-deaths-graph'),
            ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

            html.Div([
                dcc.Graph(id='daily-new-cases-graph'),
                dcc.Graph(id='daily-new-deaths-graph'),
            ], style={'width': '48%', 'display': 'inline-block'}),
        ])
    ])

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
        if not isinstance(selected_countries, list):
            selected_countries = [selected_countries]

        filtered_df = covid_data[
            covid_data['Country'].isin(selected_countries) &
            (covid_data['Date_reported'] >= start_date) &
            (covid_data['Date_reported'] <= end_date)
        ]

        cumulative_cases_fig = px.line(
            filtered_df, 
            x='Date_reported', 
            y='Cumulative_cases', 
            color='Country',
            title='Cumulative COVID-19 Cases'
        )

        cumulative_deaths_fig = px.line(
            filtered_df, 
            x='Date_reported', 
            y='Cumulative_deaths', 
            color='Country',
            title='Cumulative COVID-19 Deaths'
        )

        daily_new_cases_fig = px.bar(
            filtered_df, 
            x='Date_reported', 
            y='New_cases', 
            color='Country',
            title='Daily New COVID-19 Cases'
        )

        daily_new_deaths_fig = px.bar(
            filtered_df, 
            x='Date_reported', 
            y='New_deaths', 
            color='Country',
            title='Daily New COVID-19 Deaths'
        )

        return cumulative_cases_fig, cumulative_deaths_fig, daily_new_cases_fig, daily_new_deaths_fig

except Exception as e:
    print(f"Error initializing dashboard: {e}")
    raise

# Run the application
if __name__ == '__main__':
    app.run_server(debug=True)