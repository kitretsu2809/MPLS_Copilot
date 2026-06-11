import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np

class MLAnomalyDetector:
    def __init__(self, window_size=200):
        self.window_size = window_size
        self.log_buffer = []
        self.model = IsolationForest(contamination=0.05, random_state=42)

    def analyze_telemetry(self, recent_logs):
        """
        Dynamically fits an Isolation Forest on the historical buffer and predicts anomalies on the latest logs.
        """
        # Append to buffer and maintain window size
        self.log_buffer.extend(recent_logs)
        if len(self.log_buffer) > self.window_size:
            self.log_buffer = self.log_buffer[-self.window_size:]

        # Need at least 20 logs to do meaningful ML
        if len(self.log_buffer) < 20:
            return ["ML Engine warming up: insufficient data for anomaly detection."]

        # Extract features for ML model
        # We handle routers and links separately as they have different feature spaces
        anomalies = []
        
        from sklearn.linear_model import LinearRegression

        # --- Router Anomalies & Forecasting ---
        router_logs = [log for log in self.log_buffer if log.get("type") == "router_metric"]
        if len(router_logs) > 10:
            df_router = pd.DataFrame(router_logs)
            features = ['cpu_usage_percent', 'ram_usage_percent']
            if all(f in df_router.columns for f in features):
                X = df_router[features].fillna(0).values
                self.model.fit(X)
                
                # Group by router to perform forecasting
                for router_id, group in df_router.groupby("router_id"):
                    if len(group) > 5:
                        # Forecast CPU
                        y_cpu = group['cpu_usage_percent'].values
                        X_time = np.arange(len(y_cpu)).reshape(-1, 1)
                        lr = LinearRegression().fit(X_time, y_cpu)
                        future_time = np.array([[len(y_cpu) + 10]]) # Predict 10 steps ahead
                        cpu_pred = lr.predict(future_time)[0]
                        if cpu_pred > 90 and y_cpu[-1] < 90:
                            anomalies.append(f"PREDICTIVE FORECAST [Router {router_id}]: CPU is currently {y_cpu[-1]}% but trending rapidly to {cpu_pred:.1f}%. Proactive intervention recommended.")

                # Predict only on the most recent logs
                recent_router_logs = [log for log in recent_logs if log.get("type") == "router_metric"]
                for log in recent_router_logs:
                    x_new = np.array([[log.get('cpu_usage_percent', 0), log.get('ram_usage_percent', 0)]])
                    prediction = self.model.predict(x_new)[0]
                    if prediction == -1: # -1 indicates anomaly
                        anomalies.append(f"ML Anomaly [Router {log['router_id']}]: Abnormal CPU ({log.get('cpu_usage_percent')}%) or RAM ({log.get('ram_usage_percent')}%)")

        # --- Link Anomalies & Forecasting ---
        link_logs = [log for log in self.log_buffer if log.get("type") == "link_metric"]
        if len(link_logs) > 10:
            df_link = pd.DataFrame(link_logs)
            features = ['latency_ms', 'packet_loss_percent', 'throughput_mbps']
            if all(f in df_link.columns for f in features):
                X = df_link[features].fillna(0).values
                self.model.fit(X)
                
                # Group by link to perform forecasting
                for name, group in df_link.groupby(["source", "target"]):
                    if len(group) > 5:
                        y_lat = group['latency_ms'].values
                        X_time = np.arange(len(y_lat)).reshape(-1, 1)
                        lr = LinearRegression().fit(X_time, y_lat)
                        lat_pred = lr.predict(np.array([[len(y_lat) + 10]]))[0]
                        if lat_pred > 150 and y_lat[-1] < 150:
                            anomalies.append(f"PREDICTIVE FORECAST [Link {name[0]}->{name[1]}]: Latency trending towards severe congestion ({lat_pred:.1f}ms). Consider rerouting traffic.")

                recent_link_logs = [log for log in recent_logs if log.get("type") == "link_metric"]
                for log in recent_link_logs:
                    x_new = np.array([[log.get('latency_ms', 0), log.get('packet_loss_percent', 0), log.get('throughput_mbps', 0)]])
                    prediction = self.model.predict(x_new)[0]
                    if prediction == -1:
                        anomalies.append(f"ML Anomaly [Link {log['source']}->{log['target']}]: Unusual traffic pattern (Latency: {log.get('latency_ms')}ms, Loss: {log.get('packet_loss_percent')}%)")

        return anomalies

# Global instance to persist state across API calls
detector = MLAnomalyDetector(window_size=200)

def analyze_telemetry(logs):
    """Entry point matching the previous heuristic signature"""
    return detector.analyze_telemetry(logs)
