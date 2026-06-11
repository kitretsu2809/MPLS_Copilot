from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from agent_engine.anomaly_detector import analyze_telemetry
import os
import json
import logging

# Set up tools
@tool
def reroute_traffic(source_router: str, target_router: str, via_router: str, reason: str) -> str:
    """Simulates an MPLS traffic reroute command.
    Use this when a link is congested or failing.
    Args:
        source_router: The starting node ID.
        target_router: The destination node ID.
        via_router: The new intermediate node to route through.
        reason: Why you decided to use this tool (explain your reasoning).
    """
    logging.info(f"EXECUTING: Rerouting {source_router}->{target_router} via {via_router}. Reason: {reason}")
    return f"SUCCESS: Rerouted via {via_router}."

@tool
def reboot_router(router_id: str, reason: str) -> str:
    """Simulates a remote reboot command to a network router.
    Use this when a router has extremely high CPU/RAM usage.
    Args:
        router_id: The ID of the router to reboot (e.g. 'R1')
        reason: Why you decided to use this tool.
    """
    logging.info(f"EXECUTING: Rebooting {router_id}. Reason: {reason}")
    return f"SUCCESS: Reboot command sent to {router_id}."

@tool
def isolate_node(router_id: str, reason: str) -> str:
    """Quarantines a node by shutting down its external MPLS interfaces.
    Use this if a node is behaving maliciously or dropping 100% of packets.
    Args:
        router_id: The ID of the router to isolate.
        reason: Why you decided to use this tool.
    """
    logging.info(f"EXECUTING: Isolating {router_id}. Reason: {reason}")
    return f"SUCCESS: Node {router_id} isolated."

@tool
def run_diagnostics(router_id: str, reason: str) -> str:
    """Runs a deep diagnostic trace on a router to gather routing tables and error logs.
    Use this before taking destructive action if the cause of an anomaly is unclear.
    Args:
        router_id: The ID of the router.
        reason: Why you are running diagnostics.
    """
    logging.info(f"EXECUTING: Running diagnostics on {router_id}. Reason: {reason}")
    return f"DIAGNOSTICS COMPLETE: {router_id} shows normal routing tables but excessive packet buffer drops."

@tool
def scale_link_bandwidth(source_router: str, target_router: str, new_capacity_mbps: int, reason: str) -> str:
    """Dynamically allocates more bandwidth to a congested link via SDN.
    Use this proactively if a link is trending towards severe congestion.
    Args:
        source_router: Source node ID.
        target_router: Target node ID.
        new_capacity_mbps: The new bandwidth capacity.
        reason: Why you are scaling this link.
    """
    logging.info(f"EXECUTING: Scaling link {source_router}->{target_router} to {new_capacity_mbps}Mbps. Reason: {reason}")
    return f"SUCCESS: Link {source_router}->{target_router} bandwidth scaled to {new_capacity_mbps}Mbps."

@tool
def rollback_config(router_id: str, reason: str) -> str:
    """Reverts a router to its last known good configuration state.
    Use this if a router suddenly exhibits 100% packet loss indicating a bad config update.
    Args:
        router_id: The ID of the router to rollback.
        reason: Why you are rolling back the config.
    """
    logging.info(f"EXECUTING: Rolling back config on {router_id}. Reason: {reason}")
    return f"SUCCESS: Router {router_id} rolled back to previous stable configuration."

tools = [reroute_traffic, reboot_router, isolate_node, run_diagnostics, scale_link_bandwidth, rollback_config]

# Ensure ollama is running and has this model pulled
ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
model_name = os.getenv("OLLAMA_MODEL", "gpu-agent:latest")
llm = ChatOllama(model=model_name, temperature=0, base_url=ollama_url)

# Create the ReAct Agent Graph
agent_executor = create_react_agent(llm, tools)

def process_chat(user_message: str, telemetry_context_str: str) -> tuple[str, list]:
    """
    Processes a chat message with the Air-Gapped Copilot using LangGraph Agent.
    Returns a tuple of (response_string, list_of_executed_tools).
    """
    try:
        telemetry_data = json.loads(telemetry_context_str)
        anomalies = analyze_telemetry(telemetry_data)
        
        system_prompt = f"""
You are the Air-Gapped Predictive Copilot for a secure ISRO MPLS network.
Your job is to assist network operators in diagnosing issues and maintaining secure operations.
You have the ability to execute network commands using your tools when appropriate to fix the issues.

Here is the recent network telemetry context (last 20 logs):
{telemetry_context_str}

Detected Anomalies by ML Engine (Isolation Forest):
{anomalies if anomalies else "None"}

When a user asks you to fix an issue, use the appropriate tool to execute the action, and then report back the results. If no tool is needed, provide expert analysis based ONLY on the provided context.
ALWAYS explicitly state your reason in the tool's 'reason' argument.
"""
        
        # We pass the system prompt as the first message to the graph
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response_state = agent_executor.invoke({"messages": messages})
        
        # Extract executed tools from the state's AIMessages
        executed_tools = []
        for msg in response_state["messages"]:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for t in msg.tool_calls:
                    executed_tools.append({
                        "tool": t["name"],
                        "args": t["args"]
                    })
                    
        # The final message in the state contains the agent's text response
        return response_state["messages"][-1].content, executed_tools
    except Exception as e:
        logging.error(f"Error in LangGraph: {e}")
        return f"Copilot Error (Ensure Ollama is running and model gpu-agent:latest is pulled): {str(e)}", []
