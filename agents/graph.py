import os
import google.generativeai as genai
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from tools.search_tool import search_incidents, search_rca

# Import templates
from prompts.templates import (
    AGENT_SYSTEM_PROMPT, 
    INCIDENT_ANALYSIS_PROMPT, 
    RCA_REPORT_TEMPLATE
)

# ─── BULLETPROOF API KEY PATCH ───
# We pull your AQ. key here and configure the library globally once at the file level
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

class AgentState(TypedDict):
    current_issue: str
    search_context: str
    steps_taken: List[str]
    next_action: str
    final_output: str
    rca_report: str  

def call_llm(state: AgentState) -> AgentState:
    """Node 1: Evaluates what information needs to be fetched from FAISS."""
    if not os.getenv("GEMINI_API_KEY"):
        state["final_output"] = "Error: GEMINI_API_KEY missing from environment variables."
        state["next_action"] = "end"
        return state
    
    # Corrected clean instance declaration (no api_key parameter inside here!)
    #model = genai.GenerativeModel('gemini-1.5-flash')
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    full_prompt = (
        f"{AGENT_SYSTEM_PROMPT}\n\n"
        f"LIVE ISSUE: {state['current_issue']}\n"
        f"CONTEXT THREAD:\n{state['search_context']}\n"
        f"ACTIONS TAKEN: {state['steps_taken']}\n"
    )
    response = model.generate_content(full_prompt).text.strip()
    
    if response.startswith("CALL_TOOL:"):
        state["next_action"] = "tool"
        parts = response.split("|")
        tool_name = parts[0].replace("CALL_TOOL:", "").strip()
        query_text = parts[1].replace("QUERY:", "").strip()
        state["final_output"] = f"{tool_name}:{query_text}"
    else:
        state["next_action"] = "suggest_resolution"  
    return state

def execute_tools(state: AgentState) -> AgentState:
    """Node 2: Executes FAISS Vector Data Retrieval."""
    tool_directive = state["final_output"]
    if ":" not in tool_directive:
        return state
    tool_name, query = tool_directive.split(":", 1)
    
    if tool_name == "search_incidents" and "search_incidents" not in state["steps_taken"]:
        state["search_context"] += f"\n{search_incidents(query)}"
        state["steps_taken"].append("search_incidents")
    elif tool_name == "search_rca" and "search_rca" not in state["steps_taken"]:
        state["search_context"] += f"\n{search_rca(query)}"
        state["steps_taken"].append("search_rca")
    return state

def suggest_resolution(state: AgentState) -> AgentState:
    """Node 3 (Tool 3): Uses the gathered data to deduce the fix strategy via INCIDENT_ANALYSIS_PROMPT."""
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    formatted_prompt = INCIDENT_ANALYSIS_PROMPT.format(
        current_issue=state["current_issue"],
        search_context=state["search_context"]
    )
    
    response = model.generate_content(formatted_prompt).text.strip()
    state["final_output"] = response
    state["steps_taken"].append("suggest_resolution")
    return state

def generate_rca_report(state: AgentState) -> AgentState:
    """Node 4 (Tool 4): Transforms the analysis into an executive markdown structure via RCA_REPORT_TEMPLATE."""
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    formatted_report_prompt = RCA_REPORT_TEMPLATE.format(
        current_issue=state["current_issue"],
        final_output=state["final_output"]
    )
    
    response = model.generate_content(formatted_report_prompt).text.strip()
    state["rca_report"] = response
    state["steps_taken"].append("generate_rca_report")
    return state


def router_logic(state: AgentState) -> str:
    """Decides if the graph should keep fetching data or move forward to resolution mapping."""
    if state["next_action"] == "tool":
        return "execute_tools"
    return "suggest_resolution"

def compile_agent_workflow():
    """Compiles the 4-Node pipeline with proper prompt binding."""
    workflow = StateGraph(AgentState)
    
    # Registering all 4 distinct processing phases as explicit Graph Nodes
    workflow.add_node("call_llm", call_llm)
    workflow.add_node("execute_tools", execute_tools)
    workflow.add_node("suggest_resolution", suggest_resolution)
    workflow.add_node("generate_rca_report", generate_rca_report)
    
    workflow.set_entry_point("call_llm")
    
    # Conditional branching logic
    workflow.add_conditional_edges(
        "call_llm",
        router_logic,
        {
            "execute_tools": "execute_tools",
            "suggest_resolution": "suggest_resolution"
        }
    )
    
    # Sequential execution flow pipeline
    workflow.add_edge("execute_tools", "call_llm")
    workflow.add_edge("suggest_resolution", "generate_rca_report")
    workflow.add_edge("generate_rca_report", END)
    
    return workflow.compile()