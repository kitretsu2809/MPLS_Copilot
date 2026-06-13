# Air-Gapped Predictive Copilot for Secure MPLS Networks
**ISRO Hackathon Project - PS-13**

## Overview
This project delivers a state-of-the-art **Predictive AI Copilot** designed specifically for highly secure, air-gapped MPLS (Multiprotocol Label Switching) networks. It bridges the gap between deep-learning telemetry forecasting and agentic, autonomous network remediation. 

The entire system is containerized, operates **100% locally** without requiring any external internet APIs, and utilizes a local GPU-accelerated LLM (Large Language Model) to execute simulated SDN (Software-Defined Networking) commands.

## Architecture & Approach
Our solution solves the problem statement by combining three advanced paradigms:

1. **Predictive Deep Learning (Forecasting & Anomaly Detection)**
   - Instead of waiting for a network link to fail or a router to crash, the backend utilizes **Scikit-Learn (`IsolationForest` and `LinearRegression`)**.
   - It continuously ingests a rolling window of telemetry metrics (CPU, RAM, Latency, Throughput). 
   - It mathematically calculates trend slopes and predicts failures *before* they happen (e.g., forecasting a 100% CPU crash 2 minutes in advance).

2. **Agentic AI (LangGraph ReAct Agent)**
   - We implemented a complete **ReAct (Reason + Act)** Agentic loop. 
   - The Copilot doesn't just read data; it is armed with actual python tools: `run_diagnostics`, `reboot_router`, `scale_link_bandwidth`, `reroute_traffic`, and `rollback_config`.
   - The agent is forced to explicitly state its **"Thought Process"** before executing any tool, ensuring total explainability for network operators.

3. **True Background Autonomy via WebSockets**
   - The system features a true `asyncio` background daemon that constantly monitors the predictive ML engine.
   - When a critical anomaly is forecast, the AI is silently awakened in a separate thread. It autonomously decides how to fix the issue and executes the appropriate tool.
   - The actions are instantly broadcasted via **WebSockets** to the Next.js frontend, updating the **Tool Execution Transparency Window** in real-time without any human intervention required.

---

## 1-Click Setup Instructions

### Prerequisites: Run Ollama Locally
Because this project utilizes a GPU-accelerated local LLM in an air-gapped environment, we decoupled the LLM from the Docker containers to maximize GPU performance.

1. **Install Ollama** on your host machine and ensure it is running in the background.
2. **Pull the model**: Ensure you have pulled the required model to your host machine:
```bash
ollama run gemma:4b
```
(Or whatever custom model you built, such as `gpu-agent:latest`).

### Customizing the LLM
The system is built to support **ANY local LLM** supported by Ollama. 
If you want to use a different model (like `llama3.2` or `mistral`), simply open `docker-compose.yml` and change the `OLLAMA_MODEL` environment variable under the `backend` service:
```yaml
    environment:
      # Point to the blazing-fast native host Ollama
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
      - OLLAMA_MODEL=your-custom-model-name:latest
```

### Running the Stack
Ensure Ollama is running on your host machine, then launch the Dockerized telemetry and agent stack:

Simply run:
```bash
sudo docker compose up --build
```

### Accessing the Dashboard
Once the containers are running, open your browser and navigate to:
**http://localhost:3000**

You can either interact with the Copilot manually in the chat, or step back and watch the Transparency Window light up as the Background AI autonomously detects ML anomalies and executes SDN commands to fix the network!
