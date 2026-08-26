import os
import asyncio
from google import genai
# Exact explicit import paths to resolve the Module / Name errors
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import InMemoryRunner

# ==========================================
# 1. DEFINE INDEPENDENT TOOLS
# ==========================================

def web_search_tool(query: str) -> str:
    """
    Simulates searching the web for real-time technology information.
    
    Args:
        query: The technology search query.
    """
    knowledge_base = {
        "gemini 2.5 flash features": "Gemini 2.5 Flash features extreme speed, native multimodal reasoning, and an optimized context window for agentic workflows.",
        "modern ai agent definition": "Modern AI agents use LLMs as core orchestrators to execute tool calls, reason sequentially, and break down complex tasks autonomously."
    }
    return knowledge_base.get(query.lower(), f"No direct search hits for '{query}'. Found general articles on AI evolution.")

def save_report_tool(filename: str, content: str) -> str:
    """
    Saves a completed technical report to a local file.
    
    Args:
        filename: The target name of the file (e.g., 'report.md').
        content: The text content to write.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Success: File safely written to {filename}"
    except Exception as e:
        return f"Failed to save file due to error: {str(e)}"


# ==========================================
# 2. CONFIGURE SPECIALIZED LLM AGENTS
# ==========================================

# Research Agent: Specializes in fetching data via web tools
research_agent = LlmAgent(
    name="Researcher",
    model="gemini-2.5-flash",
    instruction=(
        "You are an expert technical researcher. Your job is to extract exact, "
        "accurate facts about requested technologies. Always utilize the web_search_tool "
        "to gather technical facts before answering."
    ),
    tools=[web_search_tool]
)

# Writer Agent: Specializes in copywriting and file saving
writer_agent = LlmAgent(
    name="TechnicalWriter",
    model="gemini-2.5-flash",
    instruction=(
        "You are a technical editor. Receive raw data facts from the Researcher "
        "and format them into an elegant summary. Once complete, "
        "always use the save_report_tool to save your work to 'ai_agents_report.md'."
    ),
    tools=[save_report_tool]
)


# ==========================================
# 3. ORCHESTRATE VIA WORKFLOW PIPELINE
# ==========================================

# SequentialAgent drives the linear pipeline sequencing
orchestrator = SequentialAgent(
    name="TechStudioPipeline",
    sub_agents=[research_agent, writer_agent]
)


# ==========================================
# 4. EXECUTE THE WORKFLOW (ASYNCHRONOUS)
# ==========================================

async def run_pipeline():
    # InMemoryRunner handles state context tracking seamlessly in local memory
    runner = InMemoryRunner(agent=orchestrator, app_name="MultiAgentWorkflowApp")
    
    task_prompt = "Research 'gemini 2.5 flash features' and write a short summary report."
    
    print(f"🚀 Triggering Multi-Agent System...")
    print(f"Prompt: {task_prompt}\n")
    
    # Run debug executes the underlying multi-agent steps with verbose tracking enabled
    response = await runner.run_debug(prompt=task_prompt, verbose=True)
    
    print("\n--- Final System Response ---")
    print(response)

if __name__ == "__main__":
    # ADK runners utilize asynchronous design loops under the hood
    asyncio.run(run_pipeline())
