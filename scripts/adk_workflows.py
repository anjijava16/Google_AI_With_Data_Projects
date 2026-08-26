import os
from google import genai
from google.adk import Workflow
from google.adk.agents import Agent
from google.adk.runners import AgentRunner
from google.adk.services import InMemoryService
from google.adk.types import Event # Handles data passing between nodes

# Ensure your GEMINI_API_KEY is active in your environment variables

# =====================================================================
# 1. DEFINE DETERMINISTIC NODES (Pure Python Functions - Cost 0 Tokens)
# =====================================================================

def data_extraction_node(node_input: dict) -> Event:
    """
    Cleans up the initial user payload. Extracts the target topic.
    Returns an Event that passes data downstream to the next graph node.
    """
    user_message = node_input.get("user_query", "").strip()
    print(f"[Node: Extractor] Processing message: '{user_message}'")
    
    # Pass clean dictionary data forward
    return Event(output={"clean_topic": user_message})


def routing_node(node_input: dict) -> str:
    """
    A routing node that evaluates the previous node's output 
    and determines which edge pathway the graph should follow.
    """
    topic = node_input.get("clean_topic", "").lower()
    print(f"[Node: Router] Inspecting topic target...")
    
    if "agent" in topic or "llm" in topic:
        return "route_to_ai_expert"
    return "route_to_general_fallback"


# =====================================================================
# 2. DEFINE REASONING-HEAVY NODES (LLM Agents)
# =====================================================================

ai_expert_agent = Agent(
    name="AiExpertNode",
    model="gemini-2.5-flash",
    instructions=(
        "You are a Senior AI Architect. Provide a highly professional, "
        "one-sentence breakthrough summary explaining the user's topic."
    )
)

general_agent = Agent(
    name="GeneralNode",
    model="gemini-2.5-flash",
    instructions="Provide a basic, polite general summary of the user's request."
)


# =====================================================================
# 3. BUILD THE GRAPH WORKFLOW (The New ADK 2.0 Feature)
# =====================================================================

# Initialize the workflow graph container
my_graph_workflow = Workflow(name="TechInquiryPipeline")

# Step A: Add your nodes to the workflow graph registry
my_graph_workflow.add_node("extract", data_extraction_node)
my_graph_workflow.add_node("router", routing_node)
my_graph_workflow.add_node("ai_specialist", ai_expert_agent)
my_graph_workflow.add_node("general_handler", general_agent)

# Step B: Explicitly link nodes together using edges
# format: (From_Node, To_Node)
my_graph_workflow.add_edge("START", "extract")
my_graph_workflow.add_edge("extract", "router")

# Step C: Add Conditional Routing Edges based on the Router node's string output
my_graph_workflow.add_conditional_edges(
    "router",
    {
        "route_to_ai_expert": "ai_specialist",
        "route_to_general_fallback": "general_handler"
    }
)

# Step D: Complete the graph layout paths by routing both agents to the END node
my_graph_workflow.add_edge("ai_specialist", "END")
my_graph_workflow.add_edge("general_handler", "END")


# =====================================================================
# 4. EXECUTE THE WORKFLOW
# =====================================================================

if __name__ == "__main__":
    # Create the modern in-memory runner environment
    session_service = InMemoryService()
    runner = AgentRunner(
        app_name="AdkGraphApp",
        session_service=session_service,
        root_agent=my_graph_workflow # Root can now be a complete graph workflow
    )

    # Payload matching our starting node expectation
    payload = {"user_query": "Explain modern AI Agents"}
    
    print("🚀 Booting ADK 2.0 Graph Workflow Engine...\n")
    
    # Run the compiled graph execution
    response = runner.run(prompt=payload)
    
    print("\n--- Final Workflow Execution Output ---")
    print(response.text)
