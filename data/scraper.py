# author: skyla tran
# project name: TBD
# program name: scraper.py
# description:

import os
import csv
import requests
import pandas as pd

from hidden import TOKEN
from datetime import datetime, timedelta

# classes
# object for storing sighting info
class Sighting:
  def __init__ (self, whale_type, created, lat, lon, comment):
    self.id = 0
    self.type = whale_type
    self.created = created
    self.lat = lat
    self.lon = lon
    self.comment = comment
    
  def updateID (self, idNum):
    self.id = idNum

# method defs
# scrape and clean API pull, save to CSV and call connectSightings
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
  
  # save acartia pull to csv
  acartia.to_csv('acartiaDataPull.csv', index = False)
  
  # create connections between sightings
  connectSightings(acartia)

# using the pd df to connect whale sightings into data struct, call connection2CSV
# !!! NEED TO IMRPOVE ACCURACY OF ALGORITHM (should have stats based on whale types)
def connectSightings(acartia):
  # dictonionary for storing connections
  connections = {}
  distance_threshold = 0.075
  time_threshold = 60
  whaleCount = 0
  
  # identify potential whale travel paths
  # for each sighting in the data pull (index of the row, conent of the row)
  for index, row in acartia.iterrows():
    whaleCount += 1
    print ('whale entry: ', whaleCount)
    whale_type = row['type']
    # if we've seen the whale before
    if whale_type in connections:
      # for each value vector element to the key 'type'
      added = False
      for sightingVector in connections[whale_type]:
        # grab the last element in the independent sighting vector 
        # aka the most recent sighting of that specific independant whale
        last_sighting = sightingVector[-1]
        
        DEBUGLAT = row['latitude']
        DEBUGLON = row['longitude']
        DEBUGTIME = row['created']
        
        # calculate distance and time differences
        distance_lat = abs(float(row['latitude']) - float(last_sighting.lat))
        distance_lon = abs(float(row['longitude']) - float(last_sighting.lon))
        time_difference = row['created'] - last_sighting.created
        minutes_difference = abs(time_difference.total_seconds() // 60)
        
        # if the sighting matches all the conditions append it to the connected sightings vector
        if (distance_lat <= distance_threshold and distance_lon <= distance_threshold
            and minutes_difference <= time_threshold):
          newSighting = Sighting(row['type'], row['created'], row['latitude'], row['longitude'], row['data_source_comments'])
          sightingVector.append(newSighting)
          added = True
          print ('new connected whale sighting')
          break
      
      # if the sighting doesn't match any dependent sightings, add to the independent sightings vector
      if (not added):
        newSighting = Sighting(row['type'], row['created'], row['latitude'], row['longitude'], row['data_source_comments'])
        newSightingVector = [newSighting]
        connections[whale_type].append(newSightingVector)
        print ('new independent sighting')
      
    # if new whale type has been spotted
    else:
      # add new dictionary entry for that whale type 
      # create a new sighting, put it into a vector for connected sightings, assign that vector to the key
      newSighting = Sighting(row['type'], row['created'], row['latitude'], row['longitude'], row['data_source_comments'])
      connectedVector = [newSighting]
      valueVector = [connectedVector]
      connections[whale_type] = valueVector
      print ('new key value added: ', whale_type)
    
  # save data structure to CSV
  connections2CSV(connections)

# save data struct to CSV, assign ID to each whale
def connections2CSV (connections):
  # create destination CSV file
  csv_file = 'connectedSightings.csv'
  fieldNames = ['id', 'type', 'created', 'lat', 'lon', 'comment']
  # begin assigning ID nums for each whale
  idNum = -1;
  
  # start saving sightings w ID nums to CSV
  with open(csv_file, mode="w", newline="") as file:
    # create writer object & write header
    writer = csv.DictWriter(file, fieldnames = fieldNames)
    writer.writeheader()
    
    # for each key in the complex data struct
    for key, value in connections.items():
      # for each dependent sightings vector in independent sightings vector
      for dependentSights in value:
        # new ID number since we are on a new whale
        idNum += 1
        # each individual sighting in the dependent sightings vector
        for sighting in dependentSights:
          # update ID number
          sighting.updateID(idNum)
          # convert to dictionary row, write to csv
          row = {field: getattr(sighting, field) for field in fieldNames}
          writer.writerow(row)








# start method call chain
scrape()