# author: skyla tran
# project name: TBD
# program name: app.py
# description:

import dash
from dash import html
import pandas as pd

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



# start designing the actual website
#----------------------------------App Title------------------------------------#
app.title = 'MAREXPS whale spotting dashboard'
#----------------------------------App Layout-----------------------------------#
app.layout = html.Div(
    id = "root", 
    children = [

    ] 
)