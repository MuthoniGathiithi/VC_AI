#!/usr/bin/env python3
"""
Verification Script for Phase 4 & Phase 5 Implementation.

This script verifies that all components are properly implemented
and can be imported without errors.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def verify_phase4():
    """Verify Phase 4 implementation."""
    print("\n" + "=" * 80)
    print("VERIFYING PHASE 4: Local AI Model + MCP Routing")
    print("=" * 80)
    
    try:
        # Test 1: Import ollama_client
        print("\n[1/4] Checking scripts/ollama_client.py...")
        from scripts.ollama_client import OllamaClient, query_model
        print("  ✓ OllamaClient imported successfully")
        print("  ✓ query_model function imported successfully")
        
        # Test 2: Import prompts
        print("\n[2/4] Checking scripts/prompts.py...")
        from scripts.prompts import (
            PROMPT_TEMPLATES,
            get_prompt_template,
            format_prompt,
            get_available_modes,
            validate_mode
        )
        print("  ✓ PROMPT_TEMPLATES imported successfully")
        print(f"  ✓ Available modes: {', '.join(get_available_modes())}")
        
        # Test 3: Import MCP client
        print("\n[3/4] Checking mcp/client.py...")
        from mcp.client import MCPClient
        print("  ✓ MCPClient imported successfully")
        
        # Test 4: Check phase4_test.py
        print("\n[4/4] Checking phase4_test.py...")
        if os.path.exists("phase4_test.py"):
            print("  ✓ phase4_test.py exists")
        else:
            print("  ❌ phase4_test.py not found")
            return False
        
        print("\n✅ PHASE 4 VERIFICATION PASSED")
        return True
    
    except Exception as e:
        print(f"\n❌ PHASE 4 VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_phase5():
    """Verify Phase 5 implementation."""
    print("\n" + "=" * 80)
    print("VERIFYING PHASE 5: Main Application with CLI & Tests")
    print("=" * 80)
    
    try:
        # Test 1: Import app
        print("\n[1/3] Checking app/main.py...")
        from app.main import ITutorApp, get_app, cli_interface
        print("  ✓ ITutorApp imported successfully")
        print("  ✓ get_app function imported successfully")
        print("  ✓ cli_interface function imported successfully")
        
        # Test 2: Check test file
        print("\n[2/3] Checking tests/test_main.py...")
        if os.path.exists("tests/test_main.py"):
            print("  ✓ tests/test_main.py exists")
            # Count test functions
            with open("tests/test_main.py", 'r') as f:
                content = f.read()
                test_count = content.count("def test_")
                print(f"  ✓ Found {test_count} test functions")
        else:
            print("  ❌ tests/test_main.py not found")
            return False
        
        # Test 3: Check pytest.ini
        print("\n[3/3] Checking pytest.ini...")
        if os.path.exists("pytest.ini"):
            print("  ✓ pytest.ini exists")
        else:
            print("  ❌ pytest.ini not found")
            return False
        
        print("\n✅ PHASE 5 VERIFICATION PASSED")
        return True
    
    except Exception as e:
        print(f"\n❌ PHASE 5 VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_integration():
    """Verify integration between components."""
    print("\n" + "=" * 80)
    print("VERIFYING INTEGRATION")
    print("=" * 80)
    
    try:
        print("\n[1/3] Checking data loader...")
        from scripts.load_data import load_questions
        loader = load_questions()
        questions = loader.get_all_questions()
        print(f"  ✓ Loaded {len(questions)} questions")
        
        print("\n[2/3] Checking MCP client initialization...")
        from mcp.client import MCPClient
        client = MCPClient()
        print("  ✓ MCPClient initialized successfully")
        
        print("\n[3/3] Checking ITutorApp initialization...")
        from app.main import ITutorApp
        app = ITutorApp()
        print("  ✓ ITutorApp initialized successfully")
        
        # Get some stats
        stats = app.get_statistics()
        print(f"  ✓ Database stats: {stats['total_questions']} questions, "
              f"{stats['unique_units']} units, {stats['unique_years']} years")
        
        print("\n✅ INTEGRATION VERIFICATION PASSED")
        return True
    
    except Exception as e:
        print(f"\n❌ INTEGRATION VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_documentation():
    """Verify documentation files."""
    print("\n" + "=" * 80)
    print("VERIFYING DOCUMENTATION")
    print("=" * 80)
    
    files_to_check = [
        ("README_MVP.md", "MVP Documentation"),
        ("PHASE4_PHASE5_SUMMARY.md", "Phase 4 & 5 Summary"),
        ("DATA_QUALITY_REPORT.md", "Data Quality Report"),
        ("DEDUPLICATION_GUIDE.md", "Deduplication Guide"),
    ]
    
    all_exist = True
    for filename, description in files_to_check:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  ✓ {description}: {filename} ({size} bytes)")
        else:
            print(f"  ❌ {description}: {filename} NOT FOUND")
            all_exist = False
    
    if all_exist:
        print("\n✅ DOCUMENTATION VERIFICATION PASSED")
        return True
    else:
        print("\n❌ DOCUMENTATION VERIFICATION FAILED")
        return False


def print_summary(phase4_ok, phase5_ok, integration_ok, docs_ok):
    """Print verification summary."""
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    results = [
        ("Phase 4 Implementation", phase4_ok),
        ("Phase 5 Implementation", phase5_ok),
        ("Component Integration", integration_ok),
        ("Documentation", docs_ok),
    ]
    
    for name, status in results:
        status_str = "✅ PASS" if status else "❌ FAIL"
        print(f"  {name}: {status_str}")
    
    all_ok = all(status for _, status in results)
    
    print("\n" + "=" * 80)
    if all_ok:
        print("✅ ALL VERIFICATIONS PASSED - Implementation is complete!")
    else:
        print("❌ SOME VERIFICATIONS FAILED - Please review the errors above")
    print("=" * 80)
    
    return all_ok


def main():
    """Run all verifications."""
    print("\n" + "=" * 80)
    print("I-TUTOR IMPLEMENTATION VERIFICATION")
    print("=" * 80)
    
    # Run verifications
    phase4_ok = verify_phase4()
    phase5_ok = verify_phase5()
    integration_ok = verify_integration()
    docs_ok = verify_documentation()
    
    # Print summary
    all_ok = print_summary(phase4_ok, phase5_ok, integration_ok, docs_ok)
    
    # Print next steps
    if all_ok:
        print("\n" + "=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print("\n1. Run Phase 4 test:")
        print("   python3 phase4_test.py")
        print("\n2. Run test suite:")
        print("   pytest tests/ -v")
        print("\n3. Run with coverage:")
        print("   pytest tests/ --cov=app --cov-report=html")
        print("\n4. Start CLI interface:")
        print("   python3 app/main.py")
        print("\n5. Make sure Ollama is running:")
        print("   ollama serve")
        print("\n" + "=" * 80)
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
