# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch


def loader():

    base_device = 'F6:12:3D:BD:DE:44'

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

    es.indices.create(index='iterate-labs-local-poc',
                  body=settings, ignore=400)

    reader = open('./demo-data/Thursday_TeamA_BladeBone_Miguel_Segment2_Left.csv', 'r')

    n = 0
    for line in reader.readlines():
        splitup = line.split(',')
        datestamp = splitup[0].split(' ')
        date=datestamp[0]
        sortdate = date.split('/')
        year = '20' + sortdate[2]
        date = year + '-' + sortdate[0] + '-' + \
               sortdate[1] + 'T' + datestamp[1] + 'Z'
        # data = splitup[1]
        # datapoints = ','.join(splitup[1:])

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
        n += 1

        if n % 1000 == 0:
            print("progress: %d" % n)


if __name__ == '__main__':
    loader()
