# -*- coding: utf-8 -*-

import time
import json
from datetime import datetime
from datetime import timedelta
import numpy as np
print("test1")
from elasticsearch import Elasticsearch
print("test2")


base_device = 'F6:12:3D:BD:DE:44'

def loader():

    es = Elasticsearch(hosts=["localhost:9200"],
                       use_ssl=False,
                       verify_certs=False, timeout=60, retry_on_timeout = True)


    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "mappings": {
            "members": {
                "dynamic": "strict",
                "properties": {
                    "device": {
                        "type": "text"
                    },
                    "data": {
                        "type": "text"
                    },
                    "timestamp": {
                        "type": "date"
                    },
                }
            }
        }
    }

    
# status code 400 (index already exists)
    es.indices.create(index='iterate-labs-local-poc',
                  body=settings, ignore=400)

                  


                  
    reader = open('./demo-data/Thursday_TeamA_BladeBone_Miguel_Segment2_Left.csv', 'r'

    n=0
    for line in reader.readlines():
        splitup = line.split(',')
        datestamp = splitup[0].split(' ')
        date=datestamp[0]
        sortdate = date.split('/')
        year = '20' + sortdate[2]
        date = year + '-' + sortdate[0] + '-' + sortdate[1] + 'T' + datestamp[1] + 'Z'  
        data = splitup[1]
    #    print(date)
        datapoints = ','.join(splitup[1:])
        es = Elasticsearch(hosts=["localhost:9200"],
                   use_ssl=False,
                       verify_certs=False, timeout=60, retry_on_timeout = True)
        es.index(index="iterate-labs-local-poc",
                id=n,
                body={"timestamp": date,
                       "device": base_device,
                       "data": "{}\r\n".format(','.join(map(str, splitup[1:])))
                   }
                )
        n = n + 1    
        #print(n)
        
                
loader()
