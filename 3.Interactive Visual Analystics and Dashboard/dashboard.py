# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Load the data
spacex_df = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv')

# Get the list of launch sites for the dropdown options
launch_sites = spacex_df['Launch Site'].unique().tolist()
launch_sites_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                       [{'label': site, 'value': site} for site in launch_sites]

# Get the min and max payload mass for the RangeSlider
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Create a dash application
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard (Masoud Fattahi Bandpey)', style={'textAlign': 'center'}),
    
    # Dropdown for launch site selection
    dcc.Dropdown(id='site-dropdown',
                 options=launch_sites_options,
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True),

    # Pie chart for launch success counts
    dcc.Graph(id='success-pie-chart'),
    
    # Label and RangeSlider for payload selection placed under the pie chart
    html.Label("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={i: '{}'.format(i) for i in range(0, 10001, 1000)},
                    value=[min_payload, max_payload]),

    # Scatter plot for payload vs. outcome
    dcc.Graph(id='success-payload-scatter-chart'),
])

# Callback for the pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value')]
)
def update_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values='class', names='Launch Site', 
                     title='Total Success Launches By Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        class_counts = filtered_df['class'].value_counts().reset_index()
        class_counts.columns = ['class', 'count']
        fig = px.pie(class_counts, values='count', names='class', 
                     title=f'Total Success Launches for site {entered_site}')
    return fig

# Callback for the scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_plot(entered_site, payload_range):
    if entered_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) &
                                (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                     title='Correlation between Payload and Success for selected site(s)')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
