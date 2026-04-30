import json
import time
from kafka import KafkaConsumer

KAFKA_BROKER = "10.4.36.159:9092"

consumer = KafkaConsumer(
    'dispatch-results',
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='latest',
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    group_id='aggregator'
)

print("Central Aggregator started...")
print("Collecting results from all zone workers...\n")

total = 0
zone_counts = {"North": 0, "South": 0, "East": 0, "Downtown": 0, "West": 0}
zone_latencies = {"North": [], "South": [], "East": [], "Downtown": [], "West": []}
start_time = time.time()

for message in consumer:
    result = message.value
    zone = result['zone']
    
    zone_counts[zone] += 1
    zone_latencies[zone].append(result['latency'])
    total += 1

    if total % 100 == 0:
        elapsed = time.time() - start_time
        throughput = total / elapsed
        
        print(f"{'='*50}")
        print(f"Total Dispatched: {total} | Throughput: {throughput:.0f} req/sec")
        print(f"Zone Distribution:")
        for z, count in zone_counts.items():
            avg_lat = sum(zone_latencies[z])/len(zone_latencies[z]) if zone_latencies[z] else 0
            print(f"  {z}: {count} requests | Avg Latency: {avg_lat:.3f}s")
        print(f"{'='*50}\n")
