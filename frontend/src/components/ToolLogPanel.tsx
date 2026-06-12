"use client";

import { useEffect, useRef } from "react";

export type ToolEvent = {
  tool: string;
  args: Record<string, any>;
};

export default function ToolLogPanel({ events }: { events: ToolEvent[] }) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new events arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  return (
    <div className="flex flex-col border border-indigo-500/30 bg-slate-900/50 backdrop-blur-md rounded-xl p-4 shadow-lg w-full h-64 overflow-hidden mt-8">
      <div className="flex items-center gap-2 border-b border-white/10 pb-2 mb-2">
        <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse"></span>
        <h3 className="font-semibold text-slate-300">Tool Execution Transparency Log</h3>
      </div>
      
      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-3 pr-2 font-mono text-sm">
        {events.length === 0 ? (
          <div className="text-slate-500 italic flex items-center justify-center h-full">
            Waiting for agentic actions...
          </div>
        ) : (
          events.map((event, i) => (
            <div key={i} className="border border-emerald-500/20 bg-emerald-500/5 p-3 rounded text-slate-300">
              <div className="flex justify-between items-start mb-1">
                <span className="text-emerald-400 font-bold">[{event.tool}]</span>
                <span className="text-xs text-slate-500">Auto-executed</span>
              </div>
              <div className="grid grid-cols-[80px_1fr] gap-2 mt-2">
                <span className="text-slate-500">Parameters:</span>
                <span className="text-indigo-300">
                  {Object.entries(event.args)
                    .filter(([k]) => k !== 'reason')
                    .map(([k, v]) => `${k}=${v}`)
                    .join(", ")}
                </span>
                
                <span className="text-slate-500">Thought Process:</span>
                <span className="text-amber-200/90 italic border-l-2 border-amber-500/50 pl-2">
                  {event.args.reason || "No explicit reason provided."}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
