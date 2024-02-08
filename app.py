# author: skyla tran
# project name: TBD
# program name: app.py
# description:

import dash
from dash import html
from dash import dcc

import pandas as pd
import plotly.express as px

import sys
sys.path.insert(0, 'data')
from hidden import MAPBOX_TOKEN

# create dash application 
app = dash.Dash(
    __name__,
    meta_tags = [
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        {"name": "description", "content": "Whale Sighting Dashboard"}, 
        {"name": "news_keywords", "content": "Whale, Orca, Killer Whale, Puget Sound, Marine Exchange of Puget Sound, MAREXPS"}
        ],
    )
 # accessing flask server attribute through server variable
server = app.server



# !! add methods here as needed

px.set_mapbox_access_token(MAPBOX_TOKEN)
# loading csv file
try:
    whaleSpottings = pd.read_csv(r"data/acartiaDataPull.csv")
    print("CSV file loaded successfully.")
except FileNotFoundError:
    print("Error: CSV file not found.")
except Exception as e:
    print("An error occurred while loading the CSV file:", e)
    
# creating figure    
fig = px.scatter_mapbox(whaleSpottings, lat="latitude", lon="longitude", hover_name="type", 
                        hover_data=["data_source_id", "created", "no_sighted", "data_source_comments"],
                        color_discrete_sequence=["blue"], zoom = 3, height = 300)
fig.update_layout(mapbox_style="streets")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()


# start designing the actual website
app.layout = html.Div([
    dcc.Graph(
        id = 'whale-map',
        figure = fig  # Assign fig to dcc.Graph
    )
])


# to run the program
if __name__ == '__main__':
    app.run_server(debug = False, port = 8050)