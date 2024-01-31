# author: skyla tran
# project name: TBD
# program name: scraper.py
# description:

import os
import re
import requests
import pandas as pd

def scrape(acartia_path='./data/'):
  # acartia token
  token = os.environ['ACARTIA_TOKEN_HERE']
  
  # acartia API call
  url='https://acartia.io/api/v1/sightings/'
  response = requests.get(url, headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
  
  # saving to pandas dataframe (basically a table)
  acartia = pd.DataFrame(response.json(), 
                     columns=['type','created','trusted','entry_id','latitude','longitude','photo_url',
                              'ssemmi_id','no_sighted','data_source_witness', 'data_source_comments'])
  
  acartia = acartia[['type','created','latitude','longitude','no_sighted','data_source_id','data_source_comments']]
  acartia = acartia.drop_duplicates()
  acartia = acartia.sort_values(by=['created'])
  
  # acartia to csv
  acartia.to_csv(acartia_path+'acartia.csv', index=False)

scrape()

