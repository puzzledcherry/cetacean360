# author: skyla tran
# project name: cetacean 360
# program name: scraper.py

import os
import csv
import json
import requests
import pandas as pd
from datetime import datetime, timedelta

# ! secrets frenzy
# if running with the hidden.py file, use direct secrets import
# if running with cron job on github actions, use env secrets import
# should match the secret type of app.py

#* DIRECT SECRETS IMPORT
# from data.hidden import TOKEN
# token = TOKEN
#* ENV SECRETS IMPORT
token = str(os.environ.get('TOKEN'))

# classes
# *object for storing sighting info
class Sighting:
  def __init__ (self, cetacean_type, created, lat, lon, no_sighted, comment):
    self.id = 0
    self.type = cetacean_type
    self.created = created
    self.lat = lat
    self.lon = lon
    self.no_sighted = no_sighted
    self.comment = comment
    # most recent sighting of this pod = 1; not most recent = 0
    self.recent = 0

# method defs
# *scrape and clean acartia API pull, save to CSV and call connectSightings
def whaleScrape (): 
  
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
  
  # calculate 1 day ago, convert timezone to PST
  timeFrame = datetime.now() - timedelta(hours = 24)
  timeFrame = pd.Timestamp(timeFrame)
  timeFrame = timeFrame.tz_localize('America/Los_Angeles')
  
  # parsing 'created' datafield into datetime format, ignore errors
  # convert to PST, drop values from more than 1 day ago
  acartia['created'] = pd.to_datetime(acartia['created'], errors='coerce')
  acartia['created'] = acartia['created'].dt.tz_localize('UTC')
  acartia['created'] = acartia['created'].dt.tz_convert('America/Los_Angeles')
  acartia = acartia[acartia['created'] >= timeFrame]
  
  # drop duplicates, sort by most recent
  acartia = acartia.drop_duplicates()
  acartia = acartia.sort_values(by = ['created'], ascending = False)
  
  # save acartia pull to csv
  acartia.to_csv('data/acartiaDataPull.csv', index = False)
  
  # create connections between sightings
  connectSightings(acartia)

# *using the acartia df to connect whale sightings into complex data struct, call connection2CSV
def connectSightings(acartia):
  # dictonionary for storing connections
  connections = {}
  # default thresholds
  lat_threshold = 0.075
  lon_threshold = 0.075
  # adding an extra 5 minutes in case the whales dilly dally
  time_threshold = 65
  cetaceanCount = 0
  
  # identify whale travel paths
  # for each sighting in the data pull 
  for index, row in acartia.iterrows():
    cetaceanCount += 1
    cetacean_type = row['type']
    
    # if we've seen the whale before
    if cetacean_type in connections:
      added = False
      
      # assign thresholds based on whale type here
      # calculations & research can be found in figjam diagram
      if (cetacean_type == 'Gray Whale'):
        lat_threshold = 0.046
        lon_threshold = 0.073
      elif (cetacean_type == 'Orca'):
        lat_threshold = 0.067
        lon_threshold = 0.098
      else:
        lat_threshold = 0.075
        lon_threshold = 0.075
      
      # for each independent sighting vector element to the key 'type'
      for sightingVector in connections[cetacean_type]:
        # grab the last element in current independent sightings dependent sightings vector
        # aka the most recent sighting of that specific independant whale
        last_sighting = sightingVector[-1]
        
        # calculate distance and time differences (certain distance within 60 minutes)
        distance_lat = abs(float(row['latitude']) - float(last_sighting.lat))
        distance_lon = abs(float(row['longitude']) - float(last_sighting.lon))
        time_difference = row['created'] - last_sighting.created
        minutes_difference = abs(time_difference.total_seconds() // 60)
        
        # if the sighting matches all the conditions, append it to the dependent sightings vector
        if (distance_lat <= lat_threshold and distance_lon <= lon_threshold
            and minutes_difference <= time_threshold):
          newSighting = Sighting(row['type'], row['created'], row['latitude'], row['longitude'], row['no_sighted'], row['data_source_comments'])
          sightingVector.append(newSighting)
          added = True
          break
      
      # if the sighting doesn't match any dependent sightings, add to the independent sightings vector
      if (not added):
        newSighting = Sighting(row['type'], row['created'], row['latitude'], row['longitude'], row['no_sighted'], row['data_source_comments'])
        newSightingVector = [newSighting]
        connections[cetacean_type].append(newSightingVector)
      
    # if new whale type has been spotted
    else:
      # add new dictionary entry for that whale type 
      # create a new sighting, put it into a vector for connected sightings, then into independent sightings vector, 
      # then assign that vector to the key
      newSighting = Sighting(row['type'], row['created'], row['latitude'], row['longitude'], row['no_sighted'], row['data_source_comments'])
      connectedVector = [newSighting]
      valueVector = [connectedVector]
      connections[cetacean_type] = valueVector
    
  # call connections2csv, save data structure to CSV
  connections2CSV(connections)

# *save data struct to CSV, assign ID to each individual pod/whale, then call toJSON
def connections2CSV (connections):
  # create destination CSV file
  csv_file = 'data/connectedSightings.csv'
  fieldNames = ['id', 'type', 'created', 'lat', 'lon', 'no_sighted', 'comment', 'recent'] 
  idNum = -1;
  
  # start saving sightings w assigned ID nums to CSV
  with open(csv_file, mode="w", newline="") as file:
    # create writer object & write header
    writer = csv.DictWriter(file, fieldnames = fieldNames)
    writer.writeheader()
    
    # for each key in the complex data struct (whale type)
    for key, value in connections.items():
      # for each dependent sightings vector in independent sightings vector (pod/whale connected sightings)
      for dependentSights in value:
        # new ID number since we are on a new pod/whale
        idNum += 1
        # each individual sighting in the dependent sightings vector (actual individual submitted sightings)
        for index, sighting in enumerate(dependentSights):
          # update ID number
          sighting.id = idNum
          
          # check if this is the most recent/last sighting in list
          if (index == 0):
            # 1: most recent of the path, 0: not most recent of the path
            sighting.recent = 1
          
          # convert to dictionary row, write to csv
          row = {field: getattr(sighting, field) for field in fieldNames}
          writer.writerow(row)
  
  # get ready to send to signalK server
  # toJSON()

# !TO BE USED WITH AIS MAPPING BRANCH OF PROJECT
# *using the connectionsCSV and row2signalk, convert to JSON then call sendToSignalKServer
def toJSON():
  # convert CSV to a pandasDF
  df = pd.read_csv("connectedSightings.csv")
  # convert each row into JSON format
  signalk_data = df.apply(row2signalk, axis=1).tolist()
  
  # save JSON data to a file 
  with open("signalkSightings.json", "w") as file:
    json.dump(signalk_data, file, indent=4)
  
  # send to the signalK server
  sendToSignalKServer(signalk_data)

# *send JSON data to signalK server
def sendToSignalKServer (signalk_data):
  # signalk URL 
  url = "http://localhost:3000/signalk/v1/api/vessels/self"

  #loop through each sighting and send it to the server
  for update in signalk_data:
    response = requests.post(url, json=update)
    if response.status_code == 200:
        print("Data successfully sent to Signal K!")
    else:
        print(f"Failed to send data to Signal K: {response.status_code}")

# *convert pandas row into JSON
def row2signalk(row):
  return {
    "context": "environment.sightings.whales",  #! idk what this should be
    "updates": [
      {
        "timestamp": pd.to_datetime(row['created']).isoformat(),
        "values": [
          {
            "path": "environment.sightings.whales", #! idk what this should be
            "value": {
              "id": row['id'],
              "type": row['type'],
              "latitude": row['lat'],
              "longitude": row['lon'],
              "no_sighted": row['no_sighted'],
              "comment": row['comment'],
              "recent": row['recent']
            }
          }
        ]
      }
    ]
  }
  
  
  

# start method call chain
whaleScrape()