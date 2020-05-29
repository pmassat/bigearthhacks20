# -*- coding: utf-8 -*-
"""
Created on Thu May 28 11:43:10 2020

@author: Pierre Massat <pmassat@stanford.edu>

Import data from the 5-year average American Community Survey
"""

#@title Import necessary modules
# import requests, urllib
# import numpy as np
import pandas as pd
# import json

# import cufflinks as cf
# import chart_studio
# import chart_studio.plotly as py
import plotly
# import plotly.tools as tls
import plotly.graph_objs as go
# import plotly.express as px

import censusdata


#%% Set options
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.precision', 2)
pd.options.plotting.backend = "plotly"


#%% Import metrics from ACS5 tables 
def fetch_metrics(year, metrics_dict, tabletype):    
    try:
        census_metrics = censusdata.download('acs5', year,
                                        censusdata.censusgeo([('state', '06'), 
                                                               ('county', '*')]),
                                        list(metrics_dict.keys()), 
                                        tabletype=tabletype)
        print(f"{year}: done.")
        return census_metrics.rename(columns=metrics_dict, inplace=False)

    except ValueError:
        pass
    


def subject_metrics():
    # table ID for...
    unempID = 'S2301_C04'# the unemployment rate
    
    return {f'{unempID}_001E':"Unemployment_rate"}


def detail_metrics():
    # table ID for...
    popID = 'B01003'# ... the population data
    housingID = 'B25001'# ... the number of housing units 

    return {f'{popID}_001E':'Population', 
            f'{housingID}_001E':'Housing units'}


#%% Combine data from different tables

def combine_metrics(year_range):
    cal_dict_s = {}
    cal_dict_d = {}
    cal_dict = {}
    
    for year in year_range:
        cal_dict_s[year] = fetch_metrics(year, subject_metrics(), tabletype='subject')
        cal_dict_d[year] = fetch_metrics(year, detail_metrics(), tabletype='detail')
        try:
            cal_dict[year] = pd.concat([cal_dict_d[year], cal_dict_s[year]], axis=1)
        except (KeyError):
            cal_dict[year] = detail_metrics[year].copy(deep=True)
        
        # Create new columns which are deep copies of other columns
        cal_dict[year]['County'] = cal_dict[year].index.copy(deep=True)
        cal_dict[year]['cartodb_id'] = cal_dict[year]['Population'].copy(deep=True)
    
        for idx in range(len(cal_dict[year])):
            try:
                cal_dict[year]['County'][idx] = cal_dict[year].index[idx].name
                cal_dict[year]['cartodb_id'][idx] = (int(cal_dict[year].index[idx].geo[1][1])+1)/2
            except AttributeError:
                break
    
        cal_dict[year]["Timestamp"] = pd.Timestamp(year=year, month=1, day=1)

    return cal_dict


def combine_years(combined_metrics):
    return pd.concat(combined_metrics, names=['Year','Censusgeo']) 


#%% Define a function that creates a figure
def create_fig(metrics_dataframe, geo_name, metrics='Population', title=None,
               yaxis_title=None):
    data = metrics_dataframe[geo_name][metrics]

    if title is None:
        title = metrics

    if yaxis_title is None:
        yaxis_title = metrics
    
    trace = go.Scatter(
        x=data.index,
        y=data.values,
        # name=f"{geo_name} County population"
    )
    layout = dict(title=f"{geo_name} County {title}", 
                  xaxis=dict(title='Year'), 
                  yaxis=dict(title=title))

    return go.Figure(trace, layout=layout)
    # return px.scatter(data, x="Year", y=metrics, 
    #                   title=f"{geo_name} County {metrics}")


#%% Function creating a figure of a variable as a function of time
def timestamp_fig(metrics_dataframe, geo_name, metrics='Population', title=None):
    data = metrics_dataframe[geo_name]

    if title is None:
        title = metrics
        
    trace = go.Scatter(x=data['Timestamp'], y=data[metrics])
    
    layout = dict(title=f"{geo_name} County {title}", 
                  xaxis=dict(title='Year'), 
                  yaxis=dict(title=title))
    
    return go.Figure(trace, layout=layout)


#%% Test plot of data

if __name__=='__main__':
    # range of years for which to import data
    year_range = range(2009,2019)
    cal_dict = combine_metrics(year_range)
    cal_metrics = combine_years(cal_dict)

#%% 
    if 'county_metrics' not in globals():
        county_metrics = {}
    county_name = 'Lake'
    county_metrics[county_name] = cal_metrics[cal_metrics['County']==''.join([county_name,' County, California'])]
    county_metrics[county_name]

    fig = timestamp_fig(county_metrics, county_name, 
                        metrics='Housing units',
                        title='Housing Units')
    # fig = px.scatter(x=data.index, y=data.values,
    #                  labels=dict(x="Year", y="Population"),
    #                  title=f"{county_name} County")
    plotly.offline.plot(fig)






