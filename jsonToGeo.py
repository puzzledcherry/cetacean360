from sys import argv
from os.path import exists
import simplejson as json 

script, in_file, out_file = argv

import urllib.request, json 
with urllib.request.urlopen("https://acartia.io/api/v1/sightings/current") as url:
    data = json.load(url)

geojson = {
    "type": "FeatureCollection",
    "features": [ 
    {
        "type": "Feature",
        "geometry" : {
            "type": "Point",
            "coordinates": [d["longitude"], d["latitude"]],
            },
        "properties" : {
            "data_source_name": d["data_source_name"],
            "data_source_entity": d["data_source_entity"],
            "created": d["created"],
            "no_sighted": d["no_sighted"],
            "type": d["type"],
            "data_source_comments": d["data_source_comments"], 
        }
     } for d in data]
}

output = open(out_file, 'w')
json.dump(geojson, output)

print (geojson)