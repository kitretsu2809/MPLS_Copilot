from fastapi import FastAPI, APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import logging
import asyncio

from agent_engine.core_graph import process_chat
from agent_engine.anomaly_detector import analyze_telemetry

app = FastAPI(title="Air-Gapped Predictive Copilot API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

router = APIRouter()

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'simulator', 'telemetry.log')

async def autonomous_monitor():
    """Background task to monitor telemetry and autonomously execute tools on anomalies."""
    while True:
        await asyncio.sleep(10)
        try:
            if not os.path.exists(LOG_FILE):
                continue
                
            with open(LOG_FILE, "r") as f:
                all_lines = f.readlines()
                recent_logs = [json.loads(line) for line in all_lines[-20:] if line.strip()]
                
            if not recent_logs:
                continue
                
            anomalies = analyze_telemetry(recent_logs)
            if anomalies:
                logging.warning(f"Background Monitor detected anomalies: {anomalies}")
                context_str = json.dumps(recent_logs)
                
                # Execute LangGraph autonomously in a separate thread so we don't block the event loop
                sys_msg = "SYSTEM ALERT: Critical anomalies detected in background monitor. Analyze and take immediate remedial action using your tools if necessary. Explain your reasoning explicitly."
                reply, executed_tools = await asyncio.to_thread(process_chat, sys_msg, context_str)
                
                # Broadcast executed tools to connected UI clients
                if executed_tools:
                    await manager.broadcast({
                        "type": "autonomous_action",
                        "tools": executed_tools,
                        "reply": reply
                    })
        except Exception as e:
            logging.error(f"Error in autonomous_monitor: {e}")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(autonomous_monitor())

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

class ChatRequest(BaseModel):
    message: str

@router.get("/telemetry")
async def get_telemetry(lines: int = 50):
    try:
        with open(LOG_FILE, "r") as f:
            all_lines = f.readlines()
            recent_logs = [json.loads(line) for line in all_lines[-lines:] if line.strip()]
            return {"telemetry": recent_logs}
    except Exception as e:
        return {"error": str(e), "telemetry": []}

@router.post("/chat")
async def chat_with_copilot(request: ChatRequest):
    try:
        # Get latest context for the LLM
        with open(LOG_FILE, "r") as f:
            all_lines = f.readlines()
            recent_logs = [json.loads(line) for line in all_lines[-20:] if line.strip()]
            
        context_str = json.dumps(recent_logs)
        reply, executed_tools = process_chat(request.message, context_str)
        return {"reply": reply, "tools": executed_tools}
    except Exception as e:
        logging.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
