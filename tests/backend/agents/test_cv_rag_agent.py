"""
Tests for backend/agents/cv_rag_agent.py

What we test:
- get_cv_rag_chain() builds a RetrievalQA chain using the vector store
- The chain uses k=4 retrieval (top 4 relevant chunks)
- The chain returns an answer when invoked

The vector store and LLM are mocked.
"""
from unittest.mock import patch, MagicMock


def test_get_cv_rag_chain_returns_retrieval_qa():
    with patch("backend.agents.cv_rag_agent.load_vectorstore") as MockVS, \
         patch("backend.agents.cv_rag_agent.get_llm") as MockLLM, \
         patch("backend.agents.cv_rag_agent.RetrievalQA") as MockQA:

        mock_retriever = MagicMock()
        MockVS.return_value.as_retriever.return_value = mock_retriever
        mock_chain = MagicMock()
        MockQA.from_chain_type.return_value = mock_chain

        from backend.agents.cv_rag_agent import get_cv_rag_chain
        result = get_cv_rag_chain()

        MockVS.assert_called_once()
        MockVS.return_value.as_retriever.assert_called_once_with(search_kwargs={"k": 4})
        MockQA.from_chain_type.assert_called_once()
        assert result is mock_chain


def test_cv_rag_chain_invocation_returns_answer():
    with patch("backend.agents.cv_rag_agent.load_vectorstore") as MockVS, \
         patch("backend.agents.cv_rag_agent.get_llm"), \
         patch("backend.agents.cv_rag_agent.RetrievalQA") as MockQA:

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"result": "Chaima has a PhD in Computer Science."}
        MockQA.from_chain_type.return_value = mock_chain
        MockVS.return_value.as_retriever.return_value = MagicMock()

        from backend.agents.cv_rag_agent import get_cv_rag_chain
        chain = get_cv_rag_chain()
        result = chain.invoke({"query": "What is Chaima's education?"})

        assert result["result"] == "Chaima has a PhD in Computer Science."


def test_cv_rag_chain_uses_stuff_chain_type():
    with patch("backend.agents.cv_rag_agent.load_vectorstore") as MockVS, \
         patch("backend.agents.cv_rag_agent.get_llm"), \
         patch("backend.agents.cv_rag_agent.RetrievalQA") as MockQA:

        MockVS.return_value.as_retriever.return_value = MagicMock()
        MockQA.from_chain_type.return_value = MagicMock()

        from backend.agents.cv_rag_agent import get_cv_rag_chain
        get_cv_rag_chain()

        call_kwargs = MockQA.from_chain_type.call_args.kwargs
        assert call_kwargs["chain_type"] == "stuff"
