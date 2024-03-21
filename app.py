# author: skyla tran
# project name: TBD
# program name: app.py
# description:

# dash framework imports
import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc

# panda data frame imports
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# include data subfolder to path, API tokens
import sys
sys.path.insert(0, 'data')
from hidden import MAPBOX_TOKEN
px.set_mapbox_access_token(MAPBOX_TOKEN)

# run the scraper
import scraper

# create dash application 
app = dash.Dash(__name__)
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

# limit the width of a line in the hover text
def limitLineWidth(line, max_width = 50):
    # base case
    # if the line is over the max width, find space near max
    if len(line) > max_width:
        last_space_index = line[:max_width].rfind(' ')
        # if there is a space, break there and recursive call
        if last_space_index != -1:
            return line[:last_space_index] + '<br>' + limitLineWidth(line[last_space_index+1:], max_width)
        # else, break at max then recursive call
        else:
            return line[:max_width] + '<br>' + limitLineWidth(line[max_width:], max_width)
    else:
        return line

# create map with lines connecting whale sightings
def createMap():
    # read CSV files into DFs
    acartiaDF = readCSV('data/acartiaDataPull.csv')
    connectedDF = readCSV('data/connectedSightings.csv')
    fig = go.Figure()
    
    # define map visual specs, style zoom & default center
    fig.update_layout(
        # defining size of map, might replace in css file in future
        width = 1000,
        height = 750,
        mapbox = dict(
            style = "carto-positron",
            zoom = 9,
            # center on puget sound
            center = dict(
                lat = 47.8125,
                lon = -122.4979
                )
        )
    )

    # for the sightings stored in connected sightings
    for sighting in range(len(connectedDF) - 1):
        # save curr and next sighting
        current_row = connectedDF.iloc[sighting]
        next_row = connectedDF.iloc[sighting + 1]
        
        # if the ids match, connect with a line
        if (current_row['id'] == next_row['id']):
            fig.add_trace(
                go.Scattermapbox(
                    mode = 'lines',
                    lon = [current_row['lon'], next_row['lon']],
                    lat = [current_row['lat'], next_row['lat']],
                    line = dict(width = 1,color = 'purple'),
                )
            )
    
    # create text for each row of the acartia data frame
    # used as hover text
    hover_text = acartiaDF.apply(lambda row: 
        f"{limitLineWidth(row['type'])}<br>"
        f"{limitLineWidth('Count: ' + str(row['no_sighted']))}<br>"
        f"{limitLineWidth('Created: ' + row['created'])}<br>"
        f"<br>"
        f"{limitLineWidth('Comments: ' + str(row['data_source_comments']))}",
        axis=1)
    
    # add dots for each sighting on the map
    # include hover info
    fig.add_trace(
        go.Scattermapbox(
            mode='markers',
            lon = acartiaDF['longitude'],
            lat = acartiaDF['latitude'],
            marker = dict(size = 8, color = 'blue', opacity = 0.7),
            
            hoverinfo = 'text',
            text = hover_text,
            
            hoverlabel = dict (
                bgcolor = 'blue',
                align = 'left',
            )
        )
    )
    
    return fig

# HTML, display the map
app.layout = html.Div(
    className = 'whole-website',
    children = [
        html.Div(
            className = 'map-container',
            children = [
                dcc.Graph (
                    id = 'plot',
                    figure = createMap()
                )
            ]
        ) 
    ]
)

# to run the program
if __name__ == '__main__':
    app.run_server(debug = False, port = 8050)
