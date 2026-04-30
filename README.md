# CloudDispatch
A Scalable Distributed Real-Time Ride-Sharing Event Processing System on Cloud

## Overview
CloudDispatch is a distributed real-time event processing system deployed on 6 Jetstream2 VM instances. It uses Apache Kafka for stream ingestion with zone-based partitioning and Python-based zone workers for parallel ride-request dispatch.

## Architecture
- **CloudDispatch-Kafka** (10.4.36.159) - Kafka Broker + Producer
- **CloudDispatch-Worker-North** (10.4.36.29) — Zone Worker
- **CloudDispatch-Worker-South** (10.4.36.180) — Zone Worker
- **CloudDispatch-Worker-East** (10.4.36.104) — Zone Worker
- **CloudDispatch-Worker-Downtown** (10.4.36.222) — Zone Worker
- **CloudDispatch-Aggregator** (10.4.36.96) — Central Aggregator + Dashboard

## Tech Stack
- Apache Kafka 3.9.2 (KRaft mode)
- Python 3 + kafka-python
- Streamlit
- Jetstream2 Cloud (Ubuntu 22.04)
- Java 21 (OpenJDK)

## Scripts
- `ride_producer.py` — Generates synthetic ride requests at 11,000+ req/sec
- `zone_worker.py` — Processes zone requests and assigns drivers
- `aggregator.py` — Collects results and computes global metrics
- `dashboard.py` — Live Streamlit dashboard

## Prerequisites
- Jetstream2 account with active allocation
- 6 Ubuntu 22.04 VM instances (m3.small)
- Java 21 installed on all VMs: `sudo apt install -y openjdk-11-jdk`
- Python 3 + kafka-python on all VMs: `pip3 install kafka-python --break-system-packages`
- Apache Kafka 3.9.2 downloaded on Kafka VM:
  `wget https://archive.apache.org/dist/kafka/3.9.2/kafka_2.13-3.9.2.tgz`
  `tar -xzf kafka_2.13-3.9.2.tgz`
- Streamlit on Aggregator VM: `pip3 install streamlit --break-system-packages`

## How to Run

### 1. Start Kafka Broker
```bash
cd kafka_2.13-3.9.2
bin/kafka-server-start.sh config/kraft/server.properties
```

### 2. Start Zone Workers (on each worker VM)
```bash
python3 ~/zone_worker.py
```

### 3. Start Aggregator
```bash
python3 ~/aggregator.py
```

### 4. Start Dashboard
```bash
python3 -m streamlit run ~/dashboard.py --server.port 8501 --server.address 0.0.0.0
```

### 5. Start Producer
```bash
python3 ~/ride_producer.py
```

### 6. Open Dashboard
http://149.165.175.189:8501
## Results
| Workers | Throughput | Avg Latency |
|---|---|---|
| 1 Worker | 724 req/sec | 0.299s |
| 2 Workers | 3,778 req/sec | 0.300s |
| 4 Workers | 5,400 req/sec | 0.300s |

## Course
ENGR-E516 Engineering Cloud Computing
Indiana University Bloomington — April 2026
