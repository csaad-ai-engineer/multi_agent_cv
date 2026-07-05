"""
Builds and loads the FAISS vector store from all files in raw_data/.

Supported formats:
  - PDF  → parsed page by page with PyPDF
  - TXT  → loaded as-is
  - Images (jpg, jpeg, png, webp, tiff) → OCR via Tesseract

At startup, a hash of all raw_data/ files is compared against the stored hash.
If anything changed (new file, updated file, deleted file), the index is rebuilt
automatically before serving the first request.
"""
import hashlib
import shutil
from pathlib import Path

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS

from backend.core.llm import get_embeddings

RAW_DATA_PATH = Path(__file__).parent.parent.parent / "raw_data"
VECTORSTORE_PATH = Path(__file__).parent.parent / "data" / "faiss_index"
HASH_PATH = Path(__file__).parent.parent / "data" / "raw_data.hash"

PDF_EXTENSIONS = {".pdf"}
TXT_EXTENSIONS = {".txt", ".md"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif"}


# ---------------------------------------------------------------------------
# Hash
# ---------------------------------------------------------------------------

def _compute_hash() -> str:
    """SHA-256 over the content of every supported file in raw_data/, sorted by name."""
    h = hashlib.sha256()
    for path in sorted(RAW_DATA_PATH.iterdir()):
        if not path.is_file():
            continue
        h.update(path.name.encode())          # include filename (detects renames/deletes)
        h.update(path.read_bytes())           # include content  (detects edits)
    return h.hexdigest()


def _stored_hash() -> str | None:
    if HASH_PATH.exists():
        return HASH_PATH.read_text().strip()
    return None


def _save_hash(digest: str) -> None:
    HASH_PATH.parent.mkdir(parents=True, exist_ok=True)
    HASH_PATH.write_text(digest)


def raw_data_changed() -> bool:
    """Return True if raw_data/ content differs from the last recorded hash."""
    return _compute_hash() != _stored_hash()


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _load_pdf(path: Path) -> list[Document]:
    return PyPDFLoader(str(path)).load()


def _load_txt(path: Path) -> list[Document]:
    return TextLoader(str(path), encoding="utf-8").load()


def _load_image(path: Path) -> list[Document]:
    import pytesseract
    from PIL import Image
    text = pytesseract.image_to_string(Image.open(path)).strip()
    if not text:
        print(f"  ⚠ No text extracted from {path.name} — skipping.")
        return []
    return [Document(page_content=text, metadata={"source": str(path)})]


def _load_all() -> list[Document]:
    documents = []
    for path in sorted(RAW_DATA_PATH.iterdir()):
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        if ext in PDF_EXTENSIONS:
            print(f"  PDF  → {path.name}")
            documents.extend(_load_pdf(path))
        elif ext in TXT_EXTENSIONS:
            print(f"  TXT  → {path.name}")
            documents.extend(_load_txt(path))
        elif ext in IMAGE_EXTENSIONS:
            print(f"  IMG  → {path.name} (OCR)")
            documents.extend(_load_image(path))
        else:
            print(f"  SKIP → {path.name} (unsupported type)")
    return documents


# ---------------------------------------------------------------------------
# Build / load
# ---------------------------------------------------------------------------

def build_vectorstore() -> FAISS:
    """Load all files from raw_data/, chunk, embed, and save the FAISS index."""
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"raw_data/ folder not found at {RAW_DATA_PATH}")

    print(f"Loading files from {RAW_DATA_PATH} ...")
    documents = _load_all()

    if not documents:
        raise ValueError("No content extracted from raw_data/ — index not built.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    VECTORSTORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(VECTORSTORE_PATH))
    _save_hash(_compute_hash())
    print(f"Vector store built with {len(chunks)} chunks and saved.")
    return vectorstore


def load_vectorstore() -> FAISS:
    """Load the FAISS index, rebuilding it if raw_data/ changed or index is missing."""
    if not VECTORSTORE_PATH.exists():
        print("Vector store not found — building...")
        return build_vectorstore()

    if raw_data_changed():
        print("raw_data/ has changed — rebuilding vector store...")
        if VECTORSTORE_PATH.exists():
            shutil.rmtree(VECTORSTORE_PATH)
        return build_vectorstore()

    embeddings = get_embeddings()
    return FAISS.load_local(str(VECTORSTORE_PATH), embeddings, allow_dangerous_deserialization=True)


if __name__ == "__main__":
    if VECTORSTORE_PATH.exists():
        shutil.rmtree(VECTORSTORE_PATH)
        print("Old index deleted.")
    build_vectorstore()
