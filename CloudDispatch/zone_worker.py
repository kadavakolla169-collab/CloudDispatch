import json
import random
import time
from kafka import KafkaConsumer, KafkaProducer

ZONE = "North"
KAFKA_BROKER = "10.4.36.159:9092"

# Simulate drivers in this zone
drivers = [{"driver_id": f"driver_{i}", "lat": random.uniform(40.7, 40.9), "lon": random.uniform(-74.1, -73.9), "available": True} for i in range(50)]

consumer = KafkaConsumer(
    'ride-requests',
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='latest',
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    group_id=f'worker-{ZONE}'
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print(f"Zone Worker {ZONE} started...")
processed = 0
start_time = time.time()

for message in consumer:
    ride = message.value
    if ride['zone'] != ZONE:
        continue

    # Find nearest available driver
    available_drivers = [d for d in drivers if d['available']]
    if not available_drivers:
        continue

    driver = random.choice(available_drivers)
    latency = round(random.uniform(0.1, 0.5), 3)

    result = {
        "rider_id": ride['rider_id'],
        "driver_id": driver['driver_id'],
        "zone": ZONE,
        "latency": latency,
        "timestamp": time.time()
    }

    producer.send('dispatch-results', value=result)
    processed += 1

    if processed % 100 == 0:
        elapsed = time.time() - start_time
        rate = processed / elapsed
        print(f"[{ZONE}] Processed {processed} requests | Rate: {rate:.0f} req/sec")
