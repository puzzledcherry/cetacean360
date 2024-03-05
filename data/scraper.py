# author: skyla tran
# project name: TBD
# program name: scraper.py
# description:

import os
import requests
import pandas as pd

from hidden import TOKEN
from datetime import datetime, timedelta

class Sighting:
  def __init__ (self, type, created, lat, lon):
    self.type = type
    self.created = created
    self.lat = lat
    self.lon = lon

# method defs
def scrape (): 
  # acartia token
  token = TOKEN
  
  # calculate a week ago, remove timezone info
  weekAgo = datetime.now() - timedelta(days = 3)
  weekAgo = weekAgo.replace(tzinfo = None)
  
  # acartia API call, provide token and get JSON back
  url='https://acartia.io/api/v1/sightings/'
  response = requests.get(url, headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
  
  # saving to pandas dataframe (basically a table)
  acartia = pd.DataFrame(response.json(), 
                      columns=['type','created','profile','trusted','entry_id','latitude','longitude','photo_url','signature',
                              'ssemmi_id','no_sighted','submitter_did','data_source_id',
                              'data_source_name','ssemmi_date_added','data_source_entity', 'data_source_witness', 'data_source_comments'])
  
  # cleaning the table
  # reducing columns, dropping untrusted enteries
  acartia = acartia[['type','created','trusted','latitude','longitude','no_sighted','data_source_id','data_source_comments']]
  acartia = acartia[(acartia['trusted'] == 1)]
  
  # parsing 'created' datafield into datetime format, ignore errors
  acartia['created'] = pd.to_datetime(acartia['created'], errors='coerce')
  # remove timezone localization, drop all values from more than a week ago
  acartia['created'] = acartia['created'].dt.tz_localize(None)
  acartia = acartia[acartia['created'] >= weekAgo]
  
  # drop duplicates, sort by most recent
  acartia = acartia.drop_duplicates()
  acartia = acartia.sort_values(by = ['created'], ascending = False)
  
  # create connections between sightings
  connectSightings(acartia)

def connectSightings(acartia):
  # dictonionary for storing connections
  connections = {}
  distance_threshold = 0.05
  time_threshold = pd.Timedelta(hours = 1)
  
  # identify potential whale travel paths
  # for each sighting in the data pull (index of the row, conent of the row)
  for index, row in acartia.iterrows():
    whale_type = row['type']
    # if we've seen the whale before
    if whale_type in connections:
      # for each value vector element to the key 'type'
      for sightingVector in connections[whale_type]:
        # grab the last element in the independent sighting vector 
        # aka the most recent sighting of that specific independant whale
        last_sighting = sightingVector[-1]
        
        # calculate distance and time differences
        print(last_sighting)
        distance_lat = abs(float(row['latitude']) - float(last_sighting.lat))
        distance_lon = abs(float(row['longitude']) - float(last_sighting.lon))
        time_difference = abs(row['created'].time() - last_sighting.created.time())
        
        # if the sighting matches all the conditions append it to the connected sightings vector
        if (distance_lat <= distance_threshold and distance_lon <= distance_threshold
            and time_difference <= time_threshold):
          newSighting = Sighting(row['type'], row['created'], row['latitude'], row['longitude'])
          sightingVector.append(newSighting)
        # if the sighting doesn't match all conditions, add to the independent sightings vector
        else:
          newSighting = Sighting(row['type'], row['created'], row['latitude'], row['longitude'])
          newSightingVector = [newSighting]
          connections[whale_type].append(sightingVector)
      
    # if new whale type has been spotted
    else:
      # add new dictionary entry for that whale type 
      # create a new sighting, put it into a vector for connected sightings, assign that vector to the key
      newSighting = Sighting(row['type'], row['created'], row['latitude'], row['longitude'])
      newSightingVector = [newSighting]
      connections[whale_type] = sightingVector
    
    for key, value in connections.items():
     print(key)

  # save acartia pull to csv
  acartia.to_csv('acartiaDataPull.csv', index = False)

# method call
scrape()