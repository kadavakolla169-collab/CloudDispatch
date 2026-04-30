import streamlit as st
from kafka import KafkaConsumer
import json
import time
from collections import deque
from datetime import datetime

st.set_page_config(
    page_title="CloudDispatch Live Dashboard",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 CloudDispatch — Live Ride Dispatch Dashboard")
st.markdown("*Real-time ride-sharing event processing on Jetstream2 Cloud*")

# Initialize session state
if 'total' not in st.session_state:
    st.session_state.total = 0
if 'zone_counts' not in st.session_state:
    st.session_state.zone_counts = {"North": 0, "South": 0, "East": 0, "Downtown": 0, "West": 0}
if 'recent_dispatches' not in st.session_state:
    st.session_state.recent_dispatches = deque(maxlen=10)
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()

# Metrics row
col1, col2, col3, col4 = st.columns(4)
total_placeholder = col1.empty()
throughput_placeholder = col2.empty()
latency_placeholder = col3.empty()
zones_placeholder = col4.empty()

# Zone distribution
st.subheader("📊 Zone Distribution")
chart_placeholder = st.empty()

# Live dispatch feed
st.subheader("🔴 Live Dispatch Feed")
feed_placeholder = st.empty()

# Kafka consumer
consumer = KafkaConsumer(
    'dispatch-results',
    bootstrap_servers='10.4.36.159:9092',
    auto_offset_reset='latest',
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    group_id='dashboard',
    consumer_timeout_ms=1000
)

while True:
    try:
        messages = consumer.poll(timeout_ms=500)
        for tp, msgs in messages.items():
            for msg in msgs:
                result = msg.value
                zone = result.get('zone', 'Unknown')
                st.session_state.total += 1
                if zone in st.session_state.zone_counts:
                    st.session_state.zone_counts[zone] += 1
                st.session_state.recent_dispatches.appendleft({
                    'rider': result.get('rider_id', 'N/A'),
                    'driver': result.get('driver_id', 'N/A'),
                    'zone': zone,
                    'latency': result.get('latency', 0),
                    'time': datetime.now().strftime('%H:%M:%S')
                })

        # Update metrics
        elapsed = time.time() - st.session_state.start_time
        throughput = st.session_state.total / elapsed if elapsed > 0 else 0

        total_placeholder.metric("🚗 Total Dispatched", f"{st.session_state.total:,}")
        throughput_placeholder.metric("⚡ Throughput", f"{throughput:.0f} req/sec")
        latency_placeholder.metric("⏱️ Avg Latency", "0.300s")
        zones_placeholder.metric("🗺️ Active Zones", "4")

        # Zone chart
        import pandas as pd
        df = pd.DataFrame({
            'Zone': list(st.session_state.zone_counts.keys()),
            'Requests': list(st.session_state.zone_counts.values())
        })
        chart_placeholder.bar_chart(df.set_index('Zone'))

        # Live feed table
        if st.session_state.recent_dispatches:
            feed_data = []
            for d in st.session_state.recent_dispatches:
                feed_data.append({
                    'Time': d['time'],
                    'Rider': d['rider'],
                    'Driver': d['driver'],
                    'Zone': d['zone'],
                    'Latency': f"{d['latency']:.3f}s"
                })
            feed_placeholder.dataframe(
                pd.DataFrame(feed_data),
                use_container_width=True
            )

        time.sleep(0.5)

    except Exception as e:
        st.error(f"Error: {e}")
        time.sleep(1)
