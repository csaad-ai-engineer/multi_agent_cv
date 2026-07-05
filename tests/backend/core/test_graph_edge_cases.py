"""
Edge case and error handling tests for backend/core/graph.py
"""
import pytest
from unittest.mock import patch, MagicMock
from backend.core.graph import select_agent, AgentState


def test_build_graph_compiles_without_error():
    with patch("backend.core.graph.StateGraph") as MockStateGraph:
        mock_graph = MagicMock()
        MockStateGraph.return_value = mock_graph
        mock_graph.compile.return_value = MagicMock()

        from backend.core.graph import build_graph
        result = build_graph()

        MockStateGraph.assert_called_once()
        mock_graph.compile.assert_called_once()
        assert result is mock_graph.compile.return_value


def test_build_graph_registers_all_nodes():
    with patch("backend.core.graph.StateGraph") as MockStateGraph:
        mock_graph = MagicMock()
        MockStateGraph.return_value = mock_graph
        mock_graph.compile.return_value = MagicMock()

        from backend.core.graph import build_graph
        build_graph()

        added_nodes = [call.args[0] for call in mock_graph.add_node.call_args_list]
        assert "router_node" in added_nodes
        assert "cv_rag_node" in added_nodes
        assert "skills_node" in added_nodes
        assert "projects_node" in added_nodes
        assert "contact_node" in added_nodes


def test_build_graph_sets_router_as_entry_point():
    with patch("backend.core.graph.StateGraph") as MockStateGraph:
        mock_graph = MagicMock()
        MockStateGraph.return_value = mock_graph
        mock_graph.compile.return_value = MagicMock()

        from backend.core.graph import build_graph
        build_graph()

        mock_graph.set_entry_point.assert_called_once_with("router_node")


def test_ask_with_empty_question():
    with patch("backend.core.graph.cv_agent_graph") as MockGraph:
        MockGraph.invoke.return_value = {"question": "", "route": "cv_rag", "answer": "I need a question to help you."}

        from backend.core.graph import ask
        result = ask("")

        MockGraph.invoke.assert_called_once_with({"question": ""})
        assert isinstance(result, str)


def test_ask_with_very_long_question():
    long_question = "What are your skills? " * 500

    with patch("backend.core.graph.cv_agent_graph") as MockGraph:
        MockGraph.invoke.return_value = {"question": long_question, "route": "skills", "answer": "She knows Python."}

        from backend.core.graph import ask
        result = ask(long_question)

        assert result == "She knows Python."


def test_ask_propagates_exception_from_graph():
    with patch("backend.core.graph.cv_agent_graph") as MockGraph:
        MockGraph.invoke.side_effect = RuntimeError("graph execution failed")

        from backend.core.graph import ask
        with pytest.raises(RuntimeError, match="graph execution failed"):
            ask("What are your skills?")


def test_router_node_propagates_route_question_exception():
    with patch("backend.core.graph.route_question") as MockRoute:
        MockRoute.side_effect = Exception("LLM API timeout")

        from backend.core.graph import router_node
        state: AgentState = {"question": "Skills?", "route": "", "answer": ""}

        with pytest.raises(Exception, match="LLM API timeout"):
            router_node(state)


def test_cv_rag_node_propagates_chain_exception():
    with patch("backend.core.graph.get_cv_rag_chain") as MockChain:
        mock_chain = MagicMock()
        mock_chain.invoke.side_effect = Exception("vector store unavailable")
        MockChain.return_value = mock_chain

        from backend.core.graph import cv_rag_node
        state: AgentState = {"question": "Tell me about yourself.", "route": "cv_rag", "answer": ""}

        with pytest.raises(Exception, match="vector store unavailable"):
            cv_rag_node(state)


def test_select_agent_with_empty_route_falls_back_to_cv_rag():
    state: AgentState = {"question": "q", "route": "", "answer": ""}
    assert select_agent(state) == "cv_rag_node"
