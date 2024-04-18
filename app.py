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
import plotly.colors as plc
from datetime import datetime, timedelta

# include data subfolder to path, API tokens
import sys
sys.path.insert(0, 'data')
from hidden import MAPBOX_TOKEN
px.set_mapbox_access_token(MAPBOX_TOKEN)

# chart studio imports for pushing to cloud
import chart_studio
import chart_studio.plotly as py
from hidden import PLOTLY_TOKEN
# chart studio login
chart_studio.tools.set_credentials_file(username = 'skylatran', api_key = PLOTLY_TOKEN)
chart_studio.tools.set_config_file(world_readable=True, sharing='public')

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

# normalize time difference between sighting and now
def normalizeTimeDiff(sighting_time):
    max_time = 1440
    current_datetime = pd.Timestamp.now()
    current_datetime = current_datetime.tz_localize('America/Los_Angeles')
    time_difference = current_datetime - sighting_time
    minutes_difference = abs(time_difference.total_seconds() // 60)

    # convert difference onto a scale [0-1]
    normalized_time = minutes_difference / max_time
    
    # returning corresponding colour decimal
    # 0 is most recent, 1 is oldest
    return normalized_time

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
            style = "mapbox://styles/mapbox/streets-v12",
            zoom = 8,
            # center on puget sound
            center = dict(
                lat = 47.58675,
                lon = -122.4825
                )
        )
    )

    # creating lines
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
                    line = dict(width = 1, color = 'limegreen'),
                )
            )
    
    # creating hover text
    # create text for each row of the acartia data frame
    hover_text = acartiaDF.apply(lambda row: 
        f"{limitLineWidth(row['type'])}<br>"
        f"{limitLineWidth('Count: ' + str(row['no_sighted']))}<br>"
        f"{limitLineWidth('Created: ' + row['created'])}<br>"
        f"<br>"
        f"{limitLineWidth('Comments: ' + str(row['data_source_comments']))}"
        f"<br>"
        f"<br>"
        f"Data aggregated by Acartia",
        axis=1)
    
    # calculate normalized values of times, invert for opacity
    # now, new sightings will be closer to 1 and old sightings closer to 0
    connectedDF['created'] = pd.to_datetime(connectedDF['created'], errors='coerce')
    connectedDF['time_diff'] = [normalizeTimeDiff(df) for df in connectedDF['created']]
    connectedDF['time_diff'] = (1 - connectedDF['time_diff'])
    
    # ! DEBUG
    print("Max normalized time difference:", connectedDF['time_diff'].max())
    print("Min normalized time difference:", connectedDF['time_diff'].min())
    
    
    # creating dots (coloured)  
    # add dots for each sighting on the map, include hover info
    fig.add_trace(
        go.Scattermapbox(
            mode='markers',
            lon = acartiaDF['longitude'],
            lat = acartiaDF['latitude'],
            marker = dict(
                size = 8, 
                color = 'blue',
                opacity = connectedDF['time_diff']),
            
            hoverinfo = 'text',
            text = hover_text,
            
            hoverlabel = dict (
                bgcolor = 'blue',
                align = 'left',
            )
        )
    )
    
    fig.update_layout(showlegend = False)
    py.plot(fig, filename = 'whale-connections', auto_open = True)
    
    # return the created map with lines and hovers and dots
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
                ),
                
            ]
        ) 
    ]
)

# to run the program
if __name__ == '__main__':
    # app.run_server(debug = False, port = 8050)
    createMap()
