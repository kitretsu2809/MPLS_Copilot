"use client";
import React, { useState, useEffect } from 'react';
import { Activity, Server, ArrowRightLeft, AlertTriangle } from 'lucide-react';

export default function TelemetryDashboard() {
  const [telemetry, setTelemetry] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTelemetry = async () => {
      try {
        const res = await fetch('http://localhost:8001/api/telemetry?lines=15');
        const data = await res.json();
        if (data.telemetry) {
          setTelemetry(data.telemetry);
        }
      } catch (err) {
        console.error(err);
        setError("Failed to fetch telemetry from backend.");
      }
    };

    const interval = setInterval(fetchTelemetry, 2000);
    return () => clearInterval(interval);
  }, []);

  const routers = telemetry.filter(t => t.type === 'router_metric').slice(-4);
  const links = telemetry.filter(t => t.type === 'link_metric').slice(-4);

  return (
    <div className="flex flex-col gap-6 w-full text-white">
      <div className="flex items-center gap-3 mb-2">
        <Activity className="text-cyan-400 w-6 h-6" />
        <h2 className="text-2xl font-semibold tracking-wide text-cyan-50">Network Telemetry <span className="text-sm font-normal text-cyan-400 opacity-70 ml-2">LIVE</span></h2>
      </div>

      {error && <div className="text-red-400 text-sm">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Routers Box */}
        <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-5 shadow-2xl">
          <h3 className="text-lg text-slate-300 font-medium mb-4 flex items-center gap-2">
            <Server className="w-5 h-5 text-indigo-400" /> Core Routers
          </h3>
          <div className="flex flex-col gap-3">
            {routers.length === 0 && <div className="text-slate-500 text-sm">Waiting for data...</div>}
            {routers.map((r, i) => (
              <div key={i} className="flex justify-between items-center bg-white/5 p-3 rounded-xl border border-white/5">
                <span className="font-semibold text-slate-200">{r.router_id}</span>
                <div className="flex gap-4 text-sm text-slate-400">
                  <span className={r.cpu_usage_percent > 85 ? "text-red-400 font-bold" : ""}>CPU: {r.cpu_usage_percent}%</span>
                  <span className={r.ram_usage_percent > 90 ? "text-red-400 font-bold" : ""}>RAM: {r.ram_usage_percent}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Links Box */}
        <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-5 shadow-2xl">
          <h3 className="text-lg text-slate-300 font-medium mb-4 flex items-center gap-2">
            <ArrowRightLeft className="w-5 h-5 text-emerald-400" /> Active Links
          </h3>
          <div className="flex flex-col gap-3">
             {links.length === 0 && <div className="text-slate-500 text-sm">Waiting for data...</div>}
             {links.map((l, i) => {
               const isAnomalous = l.packet_loss_percent > 5 || l.latency_ms > 100;
               return (
                <div key={i} className={`flex flex-col bg-white/5 p-3 rounded-xl border ${isAnomalous ? 'border-red-500/50 bg-red-500/10' : 'border-white/5'}`}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-semibold text-slate-200">{l.source} <span className="text-slate-500 text-xs">➔</span> {l.target}</span>
                    {isAnomalous && <AlertTriangle className="w-4 h-4 text-red-400 animate-pulse" />}
                  </div>
                  <div className="flex gap-4 text-xs text-slate-400">
                    <span className={l.latency_ms > 100 ? "text-red-400 font-bold" : ""}>Lat: {l.latency_ms}ms</span>
                    <span className={l.packet_loss_percent > 5 ? "text-red-400 font-bold" : ""}>Drop: {l.packet_loss_percent}%</span>
                    <span>Tput: {l.throughput_mbps} Mbps</span>
                  </div>
                </div>
               )
             })}
          </div>
        </div>
      </div>
    </div>
  );
}
