# -*- coding: utf-8 -*-
"""
This script creates an Elastic Search example for loading into SAFE.

*Note*: To use this script you need to actually install Elastic Search on your
computer if you want to run this locally. Elastic Search is
essentially a database. To install: please visit: https://www.elastic.co/
and go under downloads for your specific hardware. Note that there are
installation instructions on that site as well (that I followed too, and it
worked for my MacBook Pro machine).

@ author Jesper Kristensen
Copyright 2018-
"""

__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import time
import json
from datetime import datetime
from datetime import timedelta
import numpy as np
from elasticsearch import Elasticsearch
# ^^^ the python module to work with Elastic Search

# note that we provide the hosts to connect to here, this needs to sync
# up with what your elastic search instance is running (which is localhost
# and port 9200 by defaut - this can be changed in the elastic search
# configuration file btw.):
es = Elasticsearch(hosts=["localhost:9200"],
                   use_ssl=False,
                   verify_certs=False)

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

# create an index in elasticsearch, ignore
# status code 400 (index already exists)
es.indices.create(index='iterate-labs-local-poc', ignore=400,
                  body=settings)

# Now, let's put some data into the database:
# datetimes will be serialized into the records (neat!)

# base values (we will be creating fake data and perturbing these):
base_values = np.array([4, -162.98, -10.69, -17, 6.12, 4.1, 8.1, 8.1, 1.2])
base_date = datetime.strptime('06/28/19', '%m/%d/%y')
this_date = base_date

base_device = 'F6:12:3D:BD:DE:44'

def generate_mac_address():
    this_device_last_integers = int(base_device[-2:]) + \
                                np.random.randint(-10, 10)
    return base_device[:-2] + str(this_device_last_integers)

all_device_addresses = []
print("Populating the Elastic Search database with fake data...")
for i in range(1, 10 + 1):  # put 10 entries for now

    # generate some random numbers to perturb the base values:
    these_values = base_values * np.random.rand(len(base_values))

    # now create fake date, just tick up the days:
    this_date += timedelta(days=1)
    # stringify it:
    this_date_string = datetime.strftime(this_date, '%m/%d/%y')

    # some cool code to search last X minutes...:
    # s = Search(using=es).filter('term', response=404).filter('range', timestamp={'gte': 'now-5m', 'lt': 'now'})

    # perturb device number a bit until unique:
    while True:
        this_device_address = generate_mac_address()
        if this_device_address not in all_device_addresses:
            break

    all_device_addresses.append(this_device_address)

    es.index(index="iterate-labs-local-poc",
             id=i,
             body={"timestamp": this_date,
                   "device": this_device_address,
                   "data": "{},{}\r\n".format(this_date_string,
                                              ','.join(map(str, these_values)))
                   }
             )
    time.sleep(1)

print("Done. Now querying for testing:")

for i in range(1, 10 + 1):
    # testing...
    print("Retrieving record with id {}...".format(i))
    print(es.get(index="iterate-labs-local-poc", id=i)['_source'])

# just to keep track of the randomly generated mac addresses to represent
# some hypothetical devices:
with open('all_device_addresses.json', 'w') as fd:
    json.dump({"addresses": all_device_addresses}, fd)

print("Now the Elastic Search database should be populated with records.")
print("All done!")
