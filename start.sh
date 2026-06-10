#!/bin/bash

# Ensure virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please setup first."
    exit 1
fi

echo "Starting MPLS Network Simulator..."
source venv/bin/activate
python -m simulator.generate_telemetry &
SIM_PID=$!

echo "Starting FastAPI Backend..."
uvicorn backend.main:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!

echo "Starting Next.js Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "=========================================================="
echo "All services started!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8001"
echo "Press Ctrl+C to stop all services."
echo "=========================================================="

trap "echo 'Stopping all services...'; kill $SIM_PID $BACKEND_PID $FRONTEND_PID; exit" INT TERM
wait
