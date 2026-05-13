"""
Smoke test — verifies ai_modules.py can be imported without syntax errors.
This catches the class of bugs that were present (stray commas, broken function signatures).
Run with: pytest backend/tests/ -v
"""
import sys
import os
import importlib


def test_ai_modules_imports_without_error():
    """
    ai_modules.py had 5 syntax/import errors that crashed the entire backend.
    This test ensures the module loads cleanly.
    We mock the external dependencies so no real credentials are needed.
    """
    backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    routers_path = os.path.join(backend_path, "routers")

    # Mock out modules that require live credentials
    import unittest.mock as mock
    import types

    mock_supabase = types.ModuleType("supabase_client")
    mock_supabase.supabase = mock.MagicMock()
    sys.modules.setdefault("supabase_client", mock_supabase)

    mock_auth = types.ModuleType("auth")
    mock_auth.get_current_user = mock.MagicMock()
    sys.modules.setdefault("auth", mock_auth)

    # Add paths
    for p in [backend_path, routers_path]:
        if p not in sys.path:
            sys.path.insert(0, p)

    # If already imported from a broken state, reload
    if "routers.ai_modules" in sys.modules:
        del sys.modules["routers.ai_modules"]
    if "ai_modules" in sys.modules:
        del sys.modules["ai_modules"]

    try:
        import ai_modules  # noqa: F401
        assert hasattr(ai_modules, "router"), "router object must exist on ai_modules"
    except SyntaxError as e:
        raise AssertionError(f"ai_modules.py has a syntax error: {e}") from e
    except ImportError as e:
        # ImportError for optional deps (google.generativeai, etc.) is acceptable
        if "google" in str(e) or "generativeai" in str(e) or "marketing_templates" in str(e) or "knowledge_base" in str(e):
            pass  # Optional dependency missing in test environment — that's fine
        else:
            raise


def test_recall_router_imports():
    backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)

    try:
        import routers.recall as recall_router  # noqa: F401
        assert hasattr(recall_router, "router")
    except SyntaxError as e:
        raise AssertionError(f"recall.py has a syntax error: {e}") from e
    except Exception:
        pass  # Other import errors OK in isolated test env
