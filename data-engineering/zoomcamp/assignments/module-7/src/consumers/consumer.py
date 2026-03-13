import json

from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'green-trips',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    group_id='green-trips-counter',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    consumer_timeout_ms=10000
)

count = 0
total = 0
for message in consumer:
    trip = message.value
    total += 1
    if float(trip['trip_distance']) > 5.0:
        count += 1

consumer.close()
print(f"Total trips: {total}")
print(f"Trips with distance > 5 km: {count}")
