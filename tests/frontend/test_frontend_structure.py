"""
Frontend structure tests — verify the expected files and folders exist.

These tests are language-agnostic (Python) and simply check that the
React project structure is correct before running JS tests.

Real React component tests will be in frontend/src/**/*.test.tsx
and run with: cd frontend && npm test
"""
from pathlib import Path

FRONTEND = Path(__file__).parent.parent.parent / "frontend"


def test_frontend_directory_exists():
    assert FRONTEND.exists(), "frontend/ directory must exist"


def test_src_directory_exists():
    assert (FRONTEND / "src").exists()


def test_components_directory_exists():
    assert (FRONTEND / "src" / "components").exists()


def test_hooks_directory_exists():
    assert (FRONTEND / "src" / "hooks").exists()


def test_services_directory_exists():
    assert (FRONTEND / "src" / "services").exists()


def test_package_json_exists():
    assert (FRONTEND / "package.json").exists(), \
        "Run: cd frontend && npm create vite@latest . -- --template react-ts"
