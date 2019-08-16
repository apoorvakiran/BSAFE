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

# create an index in elasticsearch, ignore
# status code 400 (index already exists)
es.indices.create(index='iterate-labs-local-poc', ignore=400)

# Now, let's put some data into the database:
# datetimes will be serialized into the records (neat!)

# base values (we will be creating fake data and perturbing these):
base_values = np.array([4, -162.98, -10.69, -17, 6.12])
base_date = datetime.strptime('06/28/19', '%m/%d/%y')
this_date = base_date

print("Populating the Elastic Search database with fake data...")
for i in range(1, 10 + 1):  # put 10 entries for now

    # generate some random numbers to perturb the base values:
    these_values = base_values * np.random.rand(len(base_values))

    # now create fake date, just tick up the days:
    this_date += timedelta(days=1)
    # stringify it:
    this_date_string = datetime.strftime(this_date, '%m/%d/%y')

    es.index(index="iterate-labs-local-poc",
             id=i,
             body={"timestamp": datetime.now(),
                   "device": "F6:12:3D:BD:DE:44",
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

print("Now the Elastic Search database should be populated with records.")
print("All done!")
