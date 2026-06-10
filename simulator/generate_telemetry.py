import json
import time
import random
from datetime import datetime
import os

TOPOLOGY_FILE = os.path.join(os.path.dirname(__file__), 'network_topology.json')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'telemetry.log')

def load_topology():
    with open(TOPOLOGY_FILE, 'r') as f:
        return json.load(f)

def generate_router_metrics(router):
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "type": "router_metric",
        "router_id": router["id"],
        "cpu_usage_percent": round(random.uniform(10, 60), 2),
        "ram_usage_percent": round(random.uniform(20, 70), 2),
        "status": "UP"
    }

def generate_link_metrics(link, inject_anomaly=False):
    latency = random.uniform(5, 20)
    packet_loss = 0.0
    
    if inject_anomaly:
        latency += random.uniform(50, 150)
        packet_loss = round(random.uniform(2, 10), 2)
        
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "type": "link_metric",
        "source": link["source"],
        "target": link["target"],
        "latency_ms": round(latency, 2),
        "packet_loss_percent": packet_loss,
        "throughput_mbps": round(random.uniform(100, 800), 2)
    }

def run_simulator():
    topology = load_topology()
    routers = topology["routers"]
    links = topology["links"]
    
    print(f"Starting MPLS Telemetry Simulator. Writing to {LOG_FILE}...")
    
    # Empty the file first
    with open(LOG_FILE, 'w') as f:
        f.write("")
        
    tick = 0
    while True:
        tick += 1
        logs = []
        
        # 5% chance to inject an anomaly on a random link every tick
        inject_anomaly = random.random() < 0.05
        anomalous_link = random.choice(links) if inject_anomaly else None
        
        for router in routers:
            logs.append(generate_router_metrics(router))
            
        for link in links:
            is_anomalous = (link == anomalous_link)
            logs.append(generate_link_metrics(link, inject_anomaly=is_anomalous))
            
        with open(LOG_FILE, 'a') as f:
            for log in logs:
                f.write(json.dumps(log) + "\n")
                
        time.sleep(2) # Stream every 2 seconds

if __name__ == "__main__":
    run_simulator()
