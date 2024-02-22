# author: skyla tran
# project name: TBD
# program name: app.py
# description:

import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc

import pandas as pd
import plotly.express as px

import sys
sys.path.insert(0, 'data')
from hidden import MAPBOX_TOKEN
px.set_mapbox_access_token(MAPBOX_TOKEN)

# create dash application 
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
 # accessing flask server attribute through server variable
server = app.server

# loading csv file into a pandas dataframe object
def readCSV(csvFilePath):
    try:
        dataFrameObject = pd.read_csv(csvFilePath)
        print("CSV file loaded successfully.")
    except FileNotFoundError:
        print("Error: CSV file not found.")
    except Exception as e:
        print("An error occurred while loading the CSV file:", e)
    return dataFrameObject

# creating whale map figure 
def createWhaleMap():  
    whaleSpottings = readCSV(r"data/acartiaDataPull.csv") 
    fig = px.scatter_mapbox(whaleSpottings, lat = "latitude", lon = "longitude", hover_name = "type", 
                            hover_data=["data_source_id", "trusted", "created", "no_sighted", "data_source_comments"],
                            color_discrete_sequence=["blue"], zoom = 7, center = {"lat": 48.1418, "lon":-122.4244})
    fig.update_layout(mapbox_style="streets")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig
# calling function
whaleMapFig = createWhaleMap()

# start designing the actual website
app.layout = html.Div(
    className = "the-whole-website",
    children = [
        html.Div(
            className = "map-and-intro-container",
            children = [
                html.Div(
                    className = "title-container",
                    children = [
                        html.H1("SEVEN DAYS"),
                        html.H1("OF"), 
                        html.H1("WHALE"),
                        html.H1("SIGHTINGS") 
                    ]
                ),
                html.Div(
                    className = "map-container",
                    children = [
                        # whale map
                        dcc.Graph(
                            className = 'whale-map',
                            figure = whaleMapFig,  # Assign fig to dcc.Graph
                        )  
                    ]
                )
            ]
        )
    ]
)


# to run the program
if __name__ == '__main__':
    app.run_server(debug = False, port = 8050)