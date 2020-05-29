# -*- coding: utf-8 -*-
"""
Created on Thu May 28 11:43:10 2020

@author: Pierre Massat <pmassat@stanford.edu>

Import data from the 5-year average American Community Survey
"""

#%% Import modules
import plotly.graph_objs as go
import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html

from acs5_metrics import create_fig, cal_metrics, year_range


#%% Create functions
# create_fig = acs5_metrics.create_fig


#%% Create metrics data
# cal_metrics = acs5_metrics.cal_metrics

if 'county_metrics' not in globals():
    county_metrics = {}
county_name = 'Alameda'
county_metrics[county_name] = cal_metrics.loc[county_name + ' County, California']
county_metrics[county_name]


#%% Create figure of metrics
pop_fig = create_fig(county_metrics, county_name, metrics='Population')
housing_fig = create_fig(county_metrics, county_name, metrics='Housing units')
unemp_fig = create_fig(county_metrics, county_name, metrics='Unemployment_rate',
                       title='Unemployment Rate (%)')


#%% Create dash app
dash_app = dash.Dash()
app = dash_app.server

dash_app.layout = html.Div(children=[
    html.H1(children='Community Recovery'),

    html.Div(children="Welcome to Community Recovery!"),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])


#%% Run app
if __name__ == '__main__':
    dash_app.run_server(debug=True, use_reloader=False)
    
    
    