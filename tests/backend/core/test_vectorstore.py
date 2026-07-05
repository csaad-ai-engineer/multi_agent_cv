"""
Tests for backend/core/vectorstore.py

What we test:
- build_vectorstore() loads the CV, splits it, embeds it, and saves to disk
- load_vectorstore() returns a FAISS instance from disk
- load_vectorstore() calls build_vectorstore() when no index exists yet

All FAISS and embedding calls are mocked.
"""
from unittest.mock import patch, MagicMock
from pathlib import Path


def test_build_vectorstore_loads_and_splits_cv():
    mock_docs = [MagicMock()]
    mock_chunks = [MagicMock(), MagicMock(), MagicMock()]
    mock_vectorstore = MagicMock()

    with patch("backend.core.vectorstore.TextLoader") as MockLoader, \
         patch("backend.core.vectorstore.RecursiveCharacterTextSplitter") as MockSplitter, \
         patch("backend.core.vectorstore.FAISS") as MockFAISS, \
         patch("backend.core.vectorstore.get_embeddings") as MockEmbed:

        MockLoader.return_value.load.return_value = mock_docs
        MockSplitter.return_value.split_documents.return_value = mock_chunks
        MockFAISS.from_documents.return_value = mock_vectorstore

        from backend.core.vectorstore import build_vectorstore
        result = build_vectorstore()

        MockLoader.return_value.load.assert_called_once()
        MockSplitter.return_value.split_documents.assert_called_once_with(mock_docs)
        MockFAISS.from_documents.assert_called_once_with(mock_chunks, MockEmbed.return_value)
        mock_vectorstore.save_local.assert_called_once()
        assert result is mock_vectorstore


def test_load_vectorstore_when_index_exists():
    with patch("backend.core.vectorstore.VECTORSTORE_PATH") as MockPath, \
         patch("backend.core.vectorstore.FAISS") as MockFAISS, \
         patch("backend.core.vectorstore.get_embeddings") as MockEmbed:

        MockPath.exists.return_value = True
        mock_vs = MagicMock()
        MockFAISS.load_local.return_value = mock_vs

        from backend.core.vectorstore import load_vectorstore
        result = load_vectorstore()

        MockFAISS.load_local.assert_called_once()
        assert result is mock_vs


def test_load_vectorstore_builds_when_missing():
    with patch("backend.core.vectorstore.VECTORSTORE_PATH") as MockPath, \
         patch("backend.core.vectorstore.build_vectorstore") as MockBuild:

        MockPath.exists.return_value = False
        mock_vs = MagicMock()
        MockBuild.return_value = mock_vs

        from backend.core.vectorstore import load_vectorstore
        result = load_vectorstore()

        MockBuild.assert_called_once()
        assert result is mock_vs
