"""
LangGraph Multi-Agent Graph — the orchestration layer.

HOW LANGGRAPH WORKS:
LangGraph models your agent system as a directed graph:
  - NODES  = functions that do work (router, agents)
  - EDGES  = connections between nodes (who calls who next)
  - STATE  = a shared dictionary that flows through every node

The flow for every user question:
  START → router_node → (conditional edge) → specialist_agent_node → END

The router reads the question, picks a route, and LangGraph automatically
jumps to the right specialist node. No manual if/else chains needed.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, END

from backend.agents.router import route_question, AgentRoute
from backend.agents.cv_rag_agent import get_cv_rag_chain
from backend.agents.skills_agent import answer_skills_question
from backend.agents.projects_agent import answer_projects_question
from backend.agents.contact_agent import answer_contact_question


# --------------------------------------------------------------------------
# STATE
# The state is a typed dictionary shared across all nodes.
# Each node can read from it and write to it.
# --------------------------------------------------------------------------
class AgentState(TypedDict):
    question: str       # the user's input
    route: str          # which agent was selected by the router
    answer: str         # the final answer to return


# --------------------------------------------------------------------------
# NODES — each is a plain function that receives state and returns updates
# --------------------------------------------------------------------------

def router_node(state: AgentState) -> AgentState:
    """Reads the question and decides which specialist agent to call."""
    route = route_question(state["question"])
    return {"route": route.value}


def cv_rag_node(state: AgentState) -> AgentState:
    """General CV Q&A using RAG retrieval."""
    chain = get_cv_rag_chain()
    result = chain.invoke({"query": state["question"]})
    return {"answer": result["result"]}


def skills_node(state: AgentState) -> AgentState:
    """Answers technical skills questions."""
    answer = answer_skills_question(state["question"])
    return {"answer": answer}


def projects_node(state: AgentState) -> AgentState:
    """Answers project-related questions."""
    answer = answer_projects_question(state["question"])
    return {"answer": answer}


def contact_node(state: AgentState) -> AgentState:
    """Answers contact and availability questions."""
    answer = answer_contact_question(state["question"])
    return {"answer": answer}


# --------------------------------------------------------------------------
# ROUTING FUNCTION — used by the conditional edge
# Returns the name of the next node to jump to based on the route in state
# --------------------------------------------------------------------------
def select_agent(state: AgentState) -> str:
    route_map = {
        AgentRoute.CV_RAG.value: "cv_rag_node",
        AgentRoute.SKILLS.value: "skills_node",
        AgentRoute.PROJECTS.value: "projects_node",
        AgentRoute.CONTACT.value: "contact_node",
    }
    return route_map.get(state["route"], "cv_rag_node")


# --------------------------------------------------------------------------
# BUILD THE GRAPH
# --------------------------------------------------------------------------
def build_graph():
    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("router_node", router_node)
    graph.add_node("cv_rag_node", cv_rag_node)
    graph.add_node("skills_node", skills_node)
    graph.add_node("projects_node", projects_node)
    graph.add_node("contact_node", contact_node)

    # Entry point: always start at the router
    graph.set_entry_point("router_node")

    # Conditional edge: after the router runs, use select_agent() to pick next node
    graph.add_conditional_edges(
        "router_node",
        select_agent,
        {
            "cv_rag_node": "cv_rag_node",
            "skills_node": "skills_node",
            "projects_node": "projects_node",
            "contact_node": "contact_node",
        },
    )

    # All specialist nodes go straight to END
    for node in ["cv_rag_node", "skills_node", "projects_node", "contact_node"]:
        graph.add_edge(node, END)

    return graph.compile()


# Singleton — compiled once and reused across requests
cv_agent_graph = build_graph()


def ask(question: str) -> str:
    """Public interface: pass a question, get an answer string back."""
    result = cv_agent_graph.invoke({"question": question})
    return result["answer"]
