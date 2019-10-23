# -*- coding: utf-8 -*-
"""
Copyright Iterate Labs, Inc.
"""
from elasticsearch import Elasticsearch


def loader():

    index = 'iterate-labs-local-poc'  # like a table
    base_device = 'F6:12:3D:BD:DE:44'

    es = Elasticsearch(hosts=["localhost:9200"],
                       use_ssl=False,
                       verify_certs=False, timeout=60, retry_on_timeout=True)

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
                    "value": {
                        "type": "text"
                    },
                    "timestamp": {
                        "type": "date"
                    },
                }
            }
        }
    }

    # clear the index first so we don't keep putting more and more data
    # there:
    es.indices.delete(index=index, ignore=[400, 404])

    # now create a new index from scratch:
    es.indices.create(index=index, body=settings, ignore=400)

    reader = open('Demos/demo-format-5/data_small.csv', 'r')

    n = 0
    for line in reader.readlines():

        splitup = line.split(',')
        datestamp = splitup[0].split(' ')
        date=datestamp[0]
        sortdate = date.split('/')
        try:
            year = '20' + sortdate[2]
        except IndexError:
            continue
        date = year + '-' + sortdate[0] + '-' + \
               sortdate[1] + 'T' + datestamp[1] + 'Z'

        es = Elasticsearch(hosts=["localhost:9200"],
                   use_ssl=False,
                       verify_certs=False, timeout=60, retry_on_timeout = True)

        es.index(index="iterate-labs-local-poc",
                id=n,
                body={"timestamp": date,
                       "device": base_device,
                       "value": "{}\r\n".format(','.join(map(str, splitup[1:])))
                   }
                )
        n += 1

        if n % 1000 == 0:
            print("progress: %d" % n)


if __name__ == '__main__':
    loader()
