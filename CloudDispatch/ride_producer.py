import json
import random
import time
from kafka import KafkaProducer

ZONES = {
    "North": {"lat": (40.7, 40.9), "lon": (-74.1, -73.9)},
    "South": {"lat": (40.5, 40.7), "lon": (-74.1, -73.9)},
    "East": {"lat": (40.6, 40.8), "lon": (-73.9, -73.7)},
    "West": {"lat": (40.6, 40.8), "lon": (-74.3, -74.1)},
    "Downtown": {"lat": (40.7, 40.75), "lon": (-74.02, -73.97)}
}

producer = KafkaProducer(
    bootstrap_servers='10.4.36.159:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Starting high-speed ride request generator...")
count = 0
start_time = time.time()

while True:
    zone = random.choice(list(ZONES.keys()))
    lat_range = ZONES[zone]["lat"]
    lon_range = ZONES[zone]["lon"]

    ride_request = {
        "rider_id": f"rider_{random.randint(1, 10000)}",
        "zone": zone,
        "pickup_lat": round(random.uniform(*lat_range), 4),
        "pickup_lon": round(random.uniform(*lon_range), 4),
        "dropoff_lat": round(random.uniform(*lat_range), 4),
        "dropoff_lon": round(random.uniform(*lon_range), 4),
        "timestamp": time.time()
    }

    producer.send('ride-requests', value=ride_request)
    count += 1

    if count % 1000 == 0:
        elapsed = time.time() - start_time
        rate = count / elapsed
        print(f"Sent {count} requests | Rate: {rate:.0f} requests/sec")
