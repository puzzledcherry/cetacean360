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
  # calculate a week ago, remove timezone info
  weekAgo = datetime.now() - timedelta(days = 7)
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

# method call
scrape()

