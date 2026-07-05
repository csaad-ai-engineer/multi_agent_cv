"""
Edge case and error handling tests for backend/core/vectorstore.py
"""
import pytest
from unittest.mock import patch, MagicMock


def test_build_vectorstore_raises_when_cv_file_not_found():
    with patch("backend.core.vectorstore.TextLoader") as MockLoader, \
         patch("backend.core.vectorstore.get_embeddings"):

        MockLoader.return_value.load.side_effect = FileNotFoundError("cv.txt not found")

        from backend.core.vectorstore import build_vectorstore
        with pytest.raises(FileNotFoundError):
            build_vectorstore()


def test_build_vectorstore_raises_on_encoding_error():
    with patch("backend.core.vectorstore.TextLoader") as MockLoader, \
         patch("backend.core.vectorstore.get_embeddings"):

        MockLoader.return_value.load.side_effect = UnicodeDecodeError(
            "utf-8", b"\xff\xfe", 0, 1, "invalid byte"
        )

        from backend.core.vectorstore import build_vectorstore
        with pytest.raises(UnicodeDecodeError):
            build_vectorstore()


def test_build_vectorstore_raises_on_save_permission_error():
    mock_docs = [MagicMock()]
    mock_chunks = [MagicMock()]
    mock_vectorstore = MagicMock()
    mock_vectorstore.save_local.side_effect = PermissionError("no write access")

    with patch("backend.core.vectorstore.TextLoader") as MockLoader, \
         patch("backend.core.vectorstore.RecursiveCharacterTextSplitter") as MockSplitter, \
         patch("backend.core.vectorstore.FAISS") as MockFAISS, \
         patch("backend.core.vectorstore.get_embeddings"):

        MockLoader.return_value.load.return_value = mock_docs
        MockSplitter.return_value.split_documents.return_value = mock_chunks
        MockFAISS.from_documents.return_value = mock_vectorstore

        from backend.core.vectorstore import build_vectorstore
        with pytest.raises(PermissionError):
            build_vectorstore()


def test_build_vectorstore_with_empty_cv_produces_zero_chunks():
    mock_vectorstore = MagicMock()

    with patch("backend.core.vectorstore.TextLoader") as MockLoader, \
         patch("backend.core.vectorstore.RecursiveCharacterTextSplitter") as MockSplitter, \
         patch("backend.core.vectorstore.FAISS") as MockFAISS, \
         patch("backend.core.vectorstore.get_embeddings"):

        MockLoader.return_value.load.return_value = [MagicMock()]
        MockSplitter.return_value.split_documents.return_value = []
        MockFAISS.from_documents.return_value = mock_vectorstore

        from backend.core.vectorstore import build_vectorstore
        result = build_vectorstore()

        MockFAISS.from_documents.assert_called_once()
        assert result is mock_vectorstore


def test_build_vectorstore_passes_correct_splitter_config():
    with patch("backend.core.vectorstore.TextLoader") as MockLoader, \
         patch("backend.core.vectorstore.RecursiveCharacterTextSplitter") as MockSplitter, \
         patch("backend.core.vectorstore.FAISS") as MockFAISS, \
         patch("backend.core.vectorstore.get_embeddings"):

        MockLoader.return_value.load.return_value = [MagicMock()]
        MockSplitter.return_value.split_documents.return_value = [MagicMock()]
        MockFAISS.from_documents.return_value = MagicMock()

        from backend.core.vectorstore import build_vectorstore
        build_vectorstore()

        MockSplitter.assert_called_once_with(chunk_size=500, chunk_overlap=100)


def test_load_vectorstore_raises_on_corrupted_faiss_index():
    with patch("backend.core.vectorstore.VECTORSTORE_PATH") as MockPath, \
         patch("backend.core.vectorstore.FAISS") as MockFAISS, \
         patch("backend.core.vectorstore.get_embeddings"):

        MockPath.exists.return_value = True
        MockFAISS.load_local.side_effect = Exception("index file corrupted")

        from backend.core.vectorstore import load_vectorstore
        with pytest.raises(Exception, match="index file corrupted"):
            load_vectorstore()


def test_load_vectorstore_passes_allow_dangerous_deserialization():
    with patch("backend.core.vectorstore.VECTORSTORE_PATH") as MockPath, \
         patch("backend.core.vectorstore.FAISS") as MockFAISS, \
         patch("backend.core.vectorstore.get_embeddings"):

        MockPath.exists.return_value = True
        MockFAISS.load_local.return_value = MagicMock()

        from backend.core.vectorstore import load_vectorstore
        load_vectorstore()

        call_args = MockFAISS.load_local.call_args
        all_args = list(call_args.args) + list(call_args.kwargs.values())
        assert True in all_args or call_args.kwargs.get("allow_dangerous_deserialization") is True
