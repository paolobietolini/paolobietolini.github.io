import json
import math
from time import time

import pandas as pd
from kafka import KafkaProducer


def json_serializer(data):
    return json.dumps(data).encode('utf-8')


url = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-10.parquet"
columns = [
    'lpep_pickup_datetime', 'lpep_dropoff_datetime',
    'PULocationID', 'DOLocationID', 'passenger_count',
    'trip_distance', 'tip_amount', 'total_amount'
]
df = pd.read_parquet(url, columns=columns)
# Fill NaN values — Flink's JSON parser cannot handle NaN
df['passenger_count'] = df['passenger_count'].fillna(0)
print(f"Loaded {len(df)} rows")

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=json_serializer
)

t0 = time()

for _, row in df.iterrows():
    message = row.to_dict()
    message['lpep_pickup_datetime'] = str(message['lpep_pickup_datetime'])
    message['lpep_dropoff_datetime'] = str(message['lpep_dropoff_datetime'])
    producer.send('green-trips', value=message)

producer.flush()

t1 = time()
print(f'took {(t1 - t0):.2f} seconds')
