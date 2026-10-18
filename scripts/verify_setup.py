"""
DYNAMO Diagnostic & Environment Verification Script
Validates Python version, environment variables, Groq credentials, LangGraph compile, and runs test suite.
"""

import sys
import os
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def print_status(step: str, success: bool, extra: str = ""):
    icon = "[OK]  " if success else "[FAIL]"
    print(f"{icon} {step:<40} {extra}")

def main():
    print("\n" + "=" * 65)
    print(" DYNAMO Environment & Pipeline Diagnostics")
    print("=" * 65 + "\n")

    # 1. Python Version
    py_ver = sys.version.split()[0]
    py_ok = sys.version_info >= (3, 11)
    print_status("Python 3.11+ Runtime", py_ok, f"(Detected: {py_ver})")

    # 2. Key Dependencies
    deps = ["fastapi", "langgraph", "langchain_groq", "pydantic", "sqlalchemy"]
    for dep in deps:
        try:
            __import__(dep)
            print_status(f"Dependency: {dep}", True)
        except ImportError:
            print_status(f"Dependency: {dep}", False, "NOT INSTALLED")

    # 3. Environment Variables
    try:
        from backend.core.config import settings
        groq_set = bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_api_key_here")
        print_status("Groq API Key Configured", groq_set, f"Model: {settings.GROQ_MODEL}")
    except Exception as e:
        print_status("Groq API Key Configured", False, str(e))

    # 4. LangGraph Compilation
    try:
        from backend.orchestrator.graph import dynamo_graph
        print_status("LangGraph StateGraph Compilation", True, f"({len(dynamo_graph.nodes)} nodes registered)")
    except Exception as e:
        print_status("LangGraph StateGraph Compilation", False, str(e))

    # 5. Unit Tests Execution
    print("\n" + "-" * 65)
    print(" Running DYNAMO Test Suite...")
    print("-" * 65)
    suite = unittest.defaultTestLoader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=1)
    test_result = runner.run(suite)

    print("\n" + "=" * 65)
    if test_result.wasSuccessful() and py_ok:
        print(" SUCCESS: DYNAMO System is Production Ready!")
    else:
        print(" WARNING: Diagnostics detected issues. Review the logs above.")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    main()
