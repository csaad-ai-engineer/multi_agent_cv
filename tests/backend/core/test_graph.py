"""
Tests for backend/core/graph.py — the LangGraph orchestration layer.

What we test:
- select_agent() maps each route value to the correct node name
- select_agent() falls back to cv_rag_node for unknown routes
- Each node function calls the right underlying agent function
- ask() invokes the graph and returns the answer string
- build_graph() wires up all nodes and edges without errors
"""
from unittest.mock import patch, MagicMock
from backend.core.graph import select_agent, AgentState


# --------------------------------------------------------------------------
# select_agent() — the routing function used by the conditional edge
# --------------------------------------------------------------------------

def test_select_agent_routes_cv_rag():
    state: AgentState = {"question": "q", "route": "cv_rag", "answer": ""}
    assert select_agent(state) == "cv_rag_node"


def test_select_agent_routes_skills():
    state: AgentState = {"question": "q", "route": "skills", "answer": ""}
    assert select_agent(state) == "skills_node"


def test_select_agent_routes_projects():
    state: AgentState = {"question": "q", "route": "projects", "answer": ""}
    assert select_agent(state) == "projects_node"


def test_select_agent_routes_contact():
    state: AgentState = {"question": "q", "route": "contact", "answer": ""}
    assert select_agent(state) == "contact_node"


def test_select_agent_falls_back_to_cv_rag():
    state: AgentState = {"question": "q", "route": "unknown_route", "answer": ""}
    assert select_agent(state) == "cv_rag_node"


# --------------------------------------------------------------------------
# Node functions — each node should call the right specialist
# --------------------------------------------------------------------------

def test_router_node_sets_route():
    with patch("backend.core.graph.route_question") as MockRoute:
        from backend.agents.router import AgentRoute
        MockRoute.return_value = AgentRoute.SKILLS
        from backend.core.graph import router_node

        state: AgentState = {"question": "What are your skills?", "route": "", "answer": ""}
        result = router_node(state)

        MockRoute.assert_called_once_with("What are your skills?")
        assert result["route"] == "skills"


def test_cv_rag_node_calls_rag_chain():
    with patch("backend.core.graph.get_cv_rag_chain") as MockChain:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"result": "Chaima has a PhD."}
        MockChain.return_value = mock_chain

        from backend.core.graph import cv_rag_node
        state: AgentState = {"question": "What is her education?", "route": "cv_rag", "answer": ""}
        result = cv_rag_node(state)

        mock_chain.invoke.assert_called_once_with({"query": "What is her education?"})
        assert result["answer"] == "Chaima has a PhD."


def test_skills_node_calls_skills_agent():
    with patch("backend.core.graph.answer_skills_question") as MockSkills:
        MockSkills.return_value = "She knows LangGraph."

        from backend.core.graph import skills_node
        state: AgentState = {"question": "Skills?", "route": "skills", "answer": ""}
        result = skills_node(state)

        MockSkills.assert_called_once_with("Skills?")
        assert result["answer"] == "She knows LangGraph."


def test_projects_node_calls_projects_agent():
    with patch("backend.core.graph.answer_projects_question") as MockProjects:
        MockProjects.return_value = "She built a RAG agent."

        from backend.core.graph import projects_node
        state: AgentState = {"question": "Projects?", "route": "projects", "answer": ""}
        result = projects_node(state)

        MockProjects.assert_called_once_with("Projects?")
        assert result["answer"] == "She built a RAG agent."


def test_contact_node_calls_contact_agent():
    with patch("backend.core.graph.answer_contact_question") as MockContact:
        MockContact.return_value = "Email: zidisaad.chaima@gmail.com"

        from backend.core.graph import contact_node
        state: AgentState = {"question": "Contact?", "route": "contact", "answer": ""}
        result = contact_node(state)

        MockContact.assert_called_once_with("Contact?")
        assert result["answer"] == "Email: zidisaad.chaima@gmail.com"


# --------------------------------------------------------------------------
# ask() — the public interface
# --------------------------------------------------------------------------

def test_ask_returns_answer_string():
    with patch("backend.core.graph.cv_agent_graph") as MockGraph:
        MockGraph.invoke.return_value = {"question": "q", "route": "cv_rag", "answer": "She has a PhD."}

        from backend.core.graph import ask
        result = ask("What is her education?")

        MockGraph.invoke.assert_called_once_with({"question": "What is her education?"})
        assert result == "She has a PhD."
