# author: skyla tran
# project name: TBD
# program name: scraper.py
# description:

import os
import requests
import pandas as pd

from hidden import TOKEN
from datetime import datetime, timedelta

# method def
def scrape (): 
  # acartia token
  token = TOKEN
  # dictonionary for storing connections
  connections = {}
  distance_threshold = 0.05
  time_threshold = pd.Timedelta(hours = 1)
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
  
  # identify potential whale travel paths
  # for each sighting in the data pull
  for index, row in acartia.iterrows():
    
    # if we've seen the whale before
    if row['type'] in connections:
      # for each value vector element to the key 'type'
      whale_type = row['type']
      for vector in connections[whale_type]:
        # grab the last element in the independent sighting vector 
        # aka the most recent sighting of that specific independant whale
        last_sighting = vector[-1]
        
        # calculate distance and time differences
        distance_lat = abs(row['latitude'] - last_sighting[3])
        distance_lon = abs(row['longitude'] - last_sighting[4])
        time_difference = abs(row['created'].time() - last_sighting[1].time())
        
        # if the sighting matches all the conditions append it to the connected sightings vector
        if (distance_lat <= distance_threshold and distance_lon <= distance_threshold
            and time_difference <= time_threshold):
          vector.append([row['type'], row['created'], row['trusted'], row['latitude'], row['longitude']])
        # if the sighting doesn't match all conditions, add to the independent sightings vector
        else:
          connections[whale_type].append([row['type'], row['created'], row['trusted'], row['latitude'], row['longitude']])
      
    # if new whale type has been spotted
    else:
      # add new dictionary entry for that whale type 
      connections[row['type']] = [row['type'], row['created'], row['trusted'], row['latitude'], row['longitude']]
    
    for key, value in connections.items():
     print(key)
    # Iterate over lists within each value list
     for sublist in value:
         print(sublist)

  # save acartia pull to csv
  acartia.to_csv('acartiaDataPull.csv', index = False)

# method call
scrape()

