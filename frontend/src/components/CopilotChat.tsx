"use client";
import React, { useState } from 'react';
import { Send, Bot, User } from 'lucide-react';
import ToolLogPanel, { ToolEvent } from './ToolLogPanel';

export default function CopilotChat({ onNewToolEvents }: { onNewToolEvents?: (events: ToolEvent[]) => void }) {
  const [messages, setMessages] = useState<{role: 'user' | 'assistant', text: string}[]>([
    {role: 'assistant', text: "Systems online. I am monitoring the MPLS telemetry. How can I assist you today?"}
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    const saved = localStorage.getItem("copilot_chat_messages");
    if (saved) {
      try { 
        const parsed = JSON.parse(saved);
        if (parsed.length > 0) setMessages(parsed);
      } catch (e) {}
    }
  }, []);

  React.useEffect(() => {
    if (messages.length > 1) {
      // Cap at 50 messages to prevent localStorage overflow (5MB limit)
      const recentMessages = messages.slice(-50);
      localStorage.setItem("copilot_chat_messages", JSON.stringify(recentMessages));
    }
  }, [messages]);

  React.useEffect(() => {
    const ws = new WebSocket('ws://localhost:8001/api/ws');
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "autonomous_action" && data.tools) {
          if (onNewToolEvents) onNewToolEvents(data.tools);
          
          if (data.reply) {
            setMessages(prev => [...prev, {role: 'assistant', text: `[BACKGROUND ALERT]: ${data.reply}`}]);
          }
        }
      } catch (err) {
        console.error("Error parsing websocket message", err);
      }
    };

    return () => ws.close();
  }, [onNewToolEvents]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, {role: 'user', text: userMsg}]);
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg })
      });
      const data = await res.json();
      setMessages(prev => [...prev, {role: 'assistant', text: data.reply || "No response."}]);
      
      if (data.tools && data.tools.length > 0) {
        if (onNewToolEvents) onNewToolEvents(data.tools);
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, {role: 'assistant', text: "Error connecting to AI Copilot Backend."}]);
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-[500px] w-full bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden shadow-2xl relative">
      <div className="bg-white/5 border-b border-white/10 p-4 flex items-center gap-3">
        <Bot className="text-cyan-400 w-6 h-6" />
        <h3 className="text-lg font-semibold text-cyan-50">Predictive Copilot</h3>
        <span className="ml-auto px-2 py-1 text-xs font-semibold bg-emerald-500/20 text-emerald-300 rounded-full border border-emerald-500/30">Air-Gapped</span>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex gap-3 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${m.role === 'user' ? 'bg-indigo-500/20 text-indigo-300' : 'bg-cyan-500/20 text-cyan-300'}`}>
              {m.role === 'user' ? <User size={16} /> : <Bot size={16} />}
            </div>
            <div className={`max-w-[80%] rounded-2xl p-3 text-sm ${m.role === 'user' ? 'bg-indigo-500/20 border border-indigo-500/30 text-indigo-50 rounded-tr-none' : 'bg-white/5 border border-white/10 text-slate-200 rounded-tl-none'}`}>
              {m.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-300 shrink-0">
              <Bot size={16} />
            </div>
            <div className="bg-white/5 border border-white/10 text-slate-400 rounded-2xl rounded-tl-none p-3 text-sm flex gap-1 items-center">
              <span className="animate-bounce">.</span><span className="animate-bounce delay-75">.</span><span className="animate-bounce delay-150">.</span>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 bg-white/5 border-t border-white/10">
        <div className="relative flex items-center">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask Copilot about network anomalies..."
            className="w-full bg-black/40 border border-white/10 rounded-xl py-3 pl-4 pr-12 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all"
          />
          <button 
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="absolute right-2 p-2 text-cyan-400 hover:text-cyan-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
