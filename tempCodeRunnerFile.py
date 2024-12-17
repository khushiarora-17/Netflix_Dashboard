import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Load dataset
netflix_data = pd.read_csv('Netflix_Userbase.csv')

# Data preprocessing
netflix_data['Join Date'] = pd.to_datetime(netflix_data['Join Date'], dayfirst=True)

# Metrics
def calculate_metrics(data):
    total_users = len(data)
    average_age = int(data['Age'].mean())
    total_revenue = int(data['Monthly Revenue'].sum())
    return total_users, average_age, total_revenue

# Netflix color palette
netflix_red = '#E50914'
netflix_black = '#141414'
netflix_white = '#FFFFFF'

# Dash app setup
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    # Header with Netflix logo
    html.Div([
        html.Img(src='https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg', style={'height': '60px', 'marginRight': '10px'}),
        html.H1('Netflix Userbase Dashboard', style={'color': netflix_red, 'fontSize': '30px', 'display': 'inline-block'})
    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'backgroundColor': netflix_black, 'padding': '20px'}),

    # Filters Section
    html.Div([
        html.Div([
            html.Label('Select Subscription Type:', style={'color': netflix_white}),
            dcc.Dropdown(
                id='subscription-filter',
                options=[{'label': sub, 'value': sub} for sub in netflix_data['Subscription Type'].unique()],
                multi=True,
                placeholder='Filter by Subscription Type',
                style={'marginBottom': '10px'}
            ),
            html.Label('Select Country:', style={'color': netflix_white}),
            dcc.Dropdown(
                id='country-filter',
                options=[{'label': country, 'value': country} for country in netflix_data['Country'].unique()],
                multi=True,
                placeholder='Filter by Country',
                style={'marginBottom': '10px'}
            ),
            html.Label('Select Age Range:', style={'color': netflix_white}),
            dcc.RangeSlider(
                id='age-filter',
                min=int(netflix_data['Age'].min()),
                max=int(netflix_data['Age'].max()),
                step=1,
                marks={i: str(i) for i in range(int(netflix_data['Age'].min()), int(netflix_data['Age'].max()) + 1, 5)},
                value=[int(netflix_data['Age'].min()), int(netflix_data['Age'].max())],
                tooltip={"placement": "bottom"}
            )
        ], style={'padding': '20px', 'backgroundColor': netflix_black, 'border': f'2px solid {netflix_red}', 'width': '100%'})
    ], style={'marginBottom': '20px'}),

    # KPI Section
    html.Div(id='kpi-container', style={'marginBottom': '50px', 'backgroundColor': netflix_black, 'padding': '20px', 'border': f'2px solid {netflix_red}', 'width': '100%'}),

    # Graphs Section
    html.Div([
        dcc.Graph(id='subscription-graph', style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(id='device-graph', style={'width': '48%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '20px'}),

    html.Div([
        dcc.Graph(id='new-users-graph', style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(id='revenue-country-graph', style={'width': '48%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '20px'}),

    html.Div([
        dcc.Graph(id='gender-graph', style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(id='age-group-graph', style={'width': '48%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '20px'})
], style={'backgroundColor': netflix_black})

# Callbacks
@app.callback(
    [
        Output('kpi-container', 'children'),
        Output('subscription-graph', 'figure'),
        Output('device-graph', 'figure'),
        Output('new-users-graph', 'figure'),
        Output('revenue-country-graph', 'figure'),
        Output('gender-graph', 'figure'),
        Output('age-group-graph', 'figure')
    ],
    [
        Input('subscription-filter', 'value'),
        Input('country-filter', 'value'),
        Input('age-filter', 'value')
    ]
)
def update_dashboard(subscription_filter, country_filter, age_filter):
    # Filter data
    filtered_data = netflix_data
    if subscription_filter:
        filtered_data = filtered_data[filtered_data['Subscription Type'].isin(subscription_filter)]
    if country_filter:
        filtered_data = filtered_data[filtered_data['Country'].isin(country_filter)]
    if age_filter:
        filtered_data = filtered_data[(filtered_data['Age'] >= age_filter[0]) & (filtered_data['Age'] <= age_filter[1])]

    # Update metrics
    total_users, average_age, total_revenue = calculate_metrics(filtered_data)
    kpi_layout = html.Div([
        html.Div([
            html.H4('Total Users', style={'color': netflix_white, 'fontSize': '18px'}),
            html.P(f"{total_users}", style={'color': netflix_red, 'fontSize': '24px'})
        ], style={'textAlign': 'center', 'width': '30%', 'display': 'inline-block'}),
        html.Div([
            html.H4('Average Age', style={'color': netflix_white, 'fontSize': '18px'}),
            html.P(f"{average_age}", style={'color': netflix_red, 'fontSize': '24px'})
        ], style={'textAlign': 'center', 'width': '30%', 'display': 'inline-block'}),
        html.Div([
            html.H4('Total Revenue', style={'color': netflix_white, 'fontSize': '18px'}),
            html.P(f"${total_revenue}", style={'color': netflix_red, 'fontSize': '24px'})
        ], style={'textAlign': 'center', 'width': '30%', 'display': 'inline-block'})
    ])

    # Update graphs
    subscription_counts = filtered_data['Subscription Type'].value_counts().reset_index()
    subscription_counts.columns = ['Subscription Type', 'Count']
    subscription_fig = px.bar(subscription_counts, 
                               x='Subscription Type', y='Count', 
                               labels={'Subscription Type': 'Subscription Type', 'Count': 'Count'},
                               title='Subscription Type Distribution',
                               template='plotly_dark',
                               color_discrete_sequence=[netflix_red])

    device_fig = px.pie(filtered_data, names='Device', title='Device Usage',
                        color_discrete_sequence=[netflix_red, '#800000', netflix_white, '#808080'],
                        template='plotly_dark')

    new_users_data = filtered_data.groupby(filtered_data['Join Date'].dt.to_period('M')).size().reset_index(name='Count')
    new_users_data['Join Date'] = new_users_data['Join Date'].astype(str)
    new_users_fig = px.line(new_users_data,
                             x='Join Date', y='Count', 
                             labels={'Join Date': 'Date', 'Count': 'New Users'},
                             title='New Users Over Time',
                             line_shape='spline',
                             template='plotly_dark',
                             color_discrete_sequence=[netflix_red])

    revenue_country_fig = px.bar(filtered_data.groupby('Country')['Monthly Revenue'].sum().reset_index(), 
                                  x='Monthly Revenue', y='Country', 
                                  orientation='h',
                                  labels={'Country': 'Country', 'Monthly Revenue': 'Revenue'},
                                  title='Revenue by Country',
                                  template='plotly_dark',
                                  color_discrete_sequence=[netflix_red])

    gender_counts = filtered_data['Gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    gender_fig = px.bar(gender_counts, 
                        x='Gender', y='Count', 
                        labels={'Gender': 'Gender', 'Count': 'Count'},
                        title='Gender Distribution',
                        template='plotly_dark',
                        color_discrete_sequence=[netflix_red])

    age_groups = pd.cut(filtered_data['Age'], bins=[0, 18, 25, 35, 50, 100], labels=['<18', '18-25', '26-35', '36-50', '50+'])
    age_group_counts = age_groups.value_counts().reset_index()
    age_group_counts.columns = ['Age Group', 'Count']
    age_group_fig = px.bar(age_group_counts, 
                            x='Age Group', y='Count', 
                            labels={'Age Group': 'Age Group', 'Count': 'Count'},
                            title='Age Group Distribution',
                            template='plotly_dark',
                            color_discrete_sequence=[netflix_red])

    return kpi_layout, subscription_fig, device_fig, new_users_fig, revenue_country_fig, gender_fig, age_group_fig

if __name__ == '__main__':
    app.run_server(debug=True)
