"""
Code to load the elastic search database as an example.

Copyright Iterate Labs, Inc.
"""

import os
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


base_device = "F5:12:3D:BD:DE:44"

index = os.getenv("ELASTIC_SEARCH_INDEX", "iterate-labs-local-poc")
host = os.getenv("ELASTIC_SEARCH_HOST")

reader = open(
    "./Demos/demo-streaming/" "Thursday_TeamA_BladeBone_Miguel_Segment2_Left.csv", "r"
)

for n, line in enumerate(reader.readlines()[0:60000]):

    if n < 388:
        continue

    splitup = line.split(",")
    datestamp = splitup[0].split(" ")
    date = datestamp[0]
    sortdate = date.split("/")
    year = "20" + sortdate[2]
    date = year + "-" + sortdate[0] + "-" + sortdate[1] + "T" + datestamp[1] + "Z"
    data = splitup[1]
    datapoints = ",".join(splitup[1:])
    awsauth = AWS4Auth(
        os.getenv("BSAFE_AWS_ACCESS_KEY"),
        os.getenv("BSAFE_AWS_SECRET_KEY"),
        os.getenv("BSAFE_AWS_REGION"),
        "es",
    )

    es = Elasticsearch(
        # hosts=[{'host': host, 'port': 443}],
        hosts=[{"host": host, "port": 9200}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=60,
        retry_on_timeout=True,
    )

    datalist = list(map(str, splitup[1:]))

    datalist = datalist[:3]  # pretend just delta values

    es.index(
        index=index,
        id=n,
        body={
            "timestamp": date,
            "device": base_device,
            "value": "{}\r\n".format(",".join(map(str, splitup[1:]))),
        },
    )
    print(f"{n}")
