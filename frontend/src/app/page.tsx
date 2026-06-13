"use client";
import { useState, useEffect } from "react";
import TelemetryDashboard from "@/components/TelemetryDashboard";
import CopilotChat from "@/components/CopilotChat";
import ToolLogPanel, { ToolEvent } from "@/components/ToolLogPanel";

export default function Home() {
  const [toolEvents, setToolEvents] = useState<ToolEvent[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem("copilot_tool_events");
    if (saved) {
      try { setToolEvents(JSON.parse(saved)); } catch (e) {}
    }
  }, []);

  useEffect(() => {
    if (toolEvents.length > 0) {
      // Cap at 100 events to prevent localStorage overflow
      const recentEvents = toolEvents.slice(-100);
      localStorage.setItem("copilot_tool_events", JSON.stringify(recentEvents));
    }
  }, [toolEvents]);

  return (
    <main className="min-h-screen p-8 max-w-7xl mx-auto flex flex-col gap-8">
      <header className="border-b border-white/10 pb-6">
        <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-indigo-400">
          ISRO MPLS Predictive Copilot
        </h1>
        <p className="text-slate-400 mt-2">Air-gapped telemetry monitoring and intelligent anomaly remediation.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Side - Dashboard */}
        <div className="lg:col-span-7 flex flex-col gap-6">
          <TelemetryDashboard />
        </div>

        {/* Right Side - Copilot Chat */}
        <div className="lg:col-span-5 flex flex-col">
          <CopilotChat onNewToolEvents={(events) => setToolEvents(prev => [...prev, ...events])} />
        </div>
      </div>

      {/* Full Width Tool Execution Transparency Window */}
      <div className="w-full">
        <ToolLogPanel events={toolEvents} />
      </div>
    </main>
  );
}
