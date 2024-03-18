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
import plotly.graph_objs as go

import sys
sys.path.insert(0, 'data')
from hidden import MAPBOX_TOKEN
px.set_mapbox_access_token(MAPBOX_TOKEN)

# create dash application 
app = dash.Dash(__name__)
# accessing flask server attribute through server variable
server = app.server

# loading csv file into a pandas dataframe object
def readCSV(csvFilePath):
    try:
        dataFrameObject = pd.read_csv(csvFilePath)
        print("CSV file loaded successfully.")
    except FileNotFoundError:
        raise FileNotFoundError("Error: CSV file not found.")
    except Exception as e:
        raise Exception("An error occurred while loading the CSV file:", e)
    return dataFrameObject

# create map with lines connecting whale sightings
def createMap():
    # read CSV files into DFs
    acartiaDF = readCSV('data/acartiaDataPull.csv')
    connectedDF = readCSV('data/connectedSightings.csv')
    
    # DEBUG
    fig = go.Figure()

    # for the sightings stored in connected sightings
    for sighting in range(len(connectedDF) - 1):
        # save curr and next sighting
        current_row = connectedDF.iloc[sighting]
        next_row = connectedDF.iloc[sighting + 1]
        
        # if the ids match, connect
        if (current_row['id'] == next_row['id']):
            fig.add_trace(
                go.Scattermapbox(
                    mode = 'lines',
                    lon = [current_row['lon'], next_row['lon']],
                    lat = [current_row['lat'], next_row['lat']],
                    line = dict(width = 1,color = 'red'),
                )
            )
        # otherise just continue
        else:
            continue
        
        
    fig.add_trace(
        go.Scattermapbox(
            mode='markers',
            lon = connectedDF['lon'],
            lat = connectedDF['lat'],
            marker = dict(size=8, color='blue', opacity=0.7),
            hoverinfo ='text',
            text = connectedDF['comment']  # Display 'id' on hover
        )
    )
    
    fig.update_layout(
        mapbox = dict(
            style = "carto-positron",
            zoom = 9,
            center = dict(
                lat = connectedDF['lat'].mean(),
                lon = connectedDF['lon'].mean()
                )
        )
    )
    
    return fig


# display the map
app.layout = html.Div(
    className = 'whole-website',
    children = [
        html.Div(
            className = 'map-container',
            children = [
                dcc.Graph (
                    id='plot',
                    figure = createMap()
                )
            ]
        ) 
    ]
)

# to run the program
if __name__ == '__main__':
    app.run_server(debug = False, port = 8050)


# creating whale map figure 
# def createWhaleMap():  
#     whaleSpottings = readCSV(r"data/acartiaDataPull.csv") 
#     fig = px.scatter_mapbox(whaleSpottings, 
#                             lat = "latitude", 
#                             lon = "longitude", 
#                             hover_name = "type", 
#                             hover_data = ["data_source_id", "trusted", "created", "no_sighted", "data_source_comments"],
#                             color_discrete_sequence = ["blue"], 
#                             zoom = 7, 
#                             center = {"lat": 48.1418, "lon":-122.4244})
    
#     fig.update_layout(mapbox_style="streets")
#     fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#     return fig
# # calling function
# whaleMapFig = createWhaleMap()




# start designing the actual website
# app.layout = html.Div(
#     className = "the-whole-website",
#     children = [
#         html.Div(
#             className = "map-and-intro-container",
#             children = [
#                 html.Div(
#                     className = "title-container",
#                     children = [
#                         html.H1("SEVEN DAYS"),
#                         html.H1("OF"), 
#                         html.H1("WHALE"),
#                         html.H1("SIGHTINGS") 
#                     ]
#                 ),
#                 html.Div(
#                     className = "map-container",
#                     children = [
#                         # whale map
#                         dcc.Graph(
#                             className = 'whale-map',
#                             figure = whaleMapFig,  # Assign fig to dcc.Graph
#                         )  
#                     ]
#                 )
#             ]
#         )
#     ]
# )
