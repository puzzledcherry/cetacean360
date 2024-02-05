# author: skyla tran
# project name: TBD
# program name: scraper.py
# description:

import os
import requests
import pandas as pd

# method def
def scrape(acartia_path='./data/'):
  # acartia token
  token = os.environ['ACARTIA_TOKEN_HERE']
  
  # acartia API call, provide token and get JSON back
  url='https://acartia.io/api/v1/sightings/'
  response = requests.get(url, headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
  
  # saving to pandas dataframe (basically a table)
  acartia = pd.DataFrame(response.json(), 
                      columns=['type','created','profile','trusted','entry_id','latitude','longitude','photo_url','signature',
                              'ssemmi_id','no_sighted','submitter_did','data_source_id',
                              'data_source_name','ssemmi_date_added','data_source_entity', 'data_source_witness', 'data_source_comments'])
  
  # cleaning the table
  # reducing columns, dropping duplicates, sorting by newest
  acartia = acartia[['type','created','latitude','longitude','no_sighted','data_source_id','data_source_comments']]
  acartia = acartia.drop_duplicates()
  acartia = acartia.sort_values(by=['created'])
  
  # acartia to csv
  acartia.to_csv(acartia_path+'acartia.csv', index=False)

# method call
scrape()

