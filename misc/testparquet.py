import s3fs
import os
import pyarrow.parquet as pq

s3 = s3fs.S3FileSystem(
    key=os.getenv("BSAFE_AWS_ACCESS_KEY"), secret=os.getenv("BSAFE_AWS_SECRET_KEY")
)

keys = [
    "2020/07/17/00/cassia-s3-prod-5-2020-07-17-00-51-52-e4965629-4671-42e1-a62f-3a4144118d94.parquet"
]
bucket = "cassia-data-parquet"

parq_list = []
for key in keys:
    thisfile = "s3://" + bucket + "/" + key
    parq_list.append(thisfile)
    assert s3.exists(thisfile)

print(parq_list)


columns = [
    "wearable_timestamp_millis",
    "wearable_timestamp",
    "value",
    "timestamp",
    "received_timestamp",
    "firmware_version",
]

# Create your dataframe
df = (
    pq.ParquetDataset(parq_list, filesystem=s3).read_pandas(columns=columns).to_pandas()
)
print(df)
