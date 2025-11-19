#!/usr/bin/env python3
"""
Test script to verify Pi Ladder Logic installation
"""

import sys
from pathlib import Path

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    
    try:
        from core.tags import TagDatabase
        print("✓ core.tags")
    except ImportError as e:
        print(f"✗ core.tags - {e}")
        return False
    
    try:
        from core.instructions import XIC, XIO, OTE, TON, CTU
        print("✓ core.instructions")
    except ImportError as e:
        print(f"✗ core.instructions - {e}")
        return False
    
    try:
        from core.runtime import PLCRuntime, LadderProgram
        print("✓ core.runtime")
    except ImportError as e:
        print(f"✗ core.runtime - {e}")
        return False
    
    try:
        from io.gpio_manager import GPIOManager
        print("✓ io.gpio_manager")
    except ImportError as e:
        print(f"✗ io.gpio_manager - {e}")
        return False
    
    return True


def test_tag_database():
    """Test tag database functionality"""
    print("\nTesting TagDatabase...")
    
    from core.tags import TagDatabase
    
    tags = TagDatabase()
    
    # Test set/get
    tags.set("TEST_TAG", True)
    assert tags.get("TEST_TAG") == True, "Set/Get failed"
    print("✓ Set/Get operations")
    
    # Test create
    tags.create("NEW_TAG", False)
    assert tags.exists("NEW_TAG"), "Create failed"
    print("✓ Create operation")
    
    # Test system tags
    assert tags.exists("_SYSTEM.SCAN_TIME"), "System tags missing"
    print("✓ System tags initialized")
    
    return True


def test_instructions():
    """Test ladder instructions"""
    print("\nTesting Instructions...")
    
    from core.tags import TagDatabase
    from core.instructions import XIC, XIO, OTE, TON
    
    tags = TagDatabase()
    
    # Test XIC
    tags.set("INPUT", True)
    xic = XIC("INPUT")
    result = xic.evaluate(tags, True)
    assert result == True, "XIC failed"
    print("✓ XIC (Examine If Closed)")
    
    # Test XIO
    tags.set("INPUT", False)
    xio = XIO("INPUT")
    result = xio.evaluate(tags, True)
    assert result == True, "XIO failed"
    print("✓ XIO (Examine If Open)")
    
    # Test OTE
    ote = OTE("OUTPUT")
    ote.evaluate(tags, True)
    assert tags.get("OUTPUT") == True, "OTE failed"
    print("✓ OTE (Output Energize)")
    
    # Test TON
    ton = TON("TIMER", 1000)
    ton.evaluate(tags, True)
    assert tags.exists("TIMER.DN"), "TON tags not created"
    print("✓ TON (Timer On Delay)")
    
    return True


def test_runtime():
    """Test runtime execution"""
    print("\nTesting PLCRuntime...")
    
    from core.runtime import PLCRuntime
    
    runtime = PLCRuntime(scan_time_ms=100)
    
    # Test program loading
    try:
        runtime.load_program("examples/blink.json")
        print("✓ Program loading")
    except Exception as e:
        print(f"✗ Program loading failed - {e}")
        return False
    
    # Test single scan
    try:
        runtime.start()
        runtime.run_scan_cycle()
        runtime.stop()
        print("✓ Scan cycle execution")
    except Exception as e:
        print(f"✗ Scan cycle failed - {e}")
        return False
    
    return True


def test_gpio_manager():
    """Test GPIO manager"""
    print("\nTesting GPIOManager...")
    
    from io.gpio_manager import GPIOManager
    
    # Should work in simulation mode
    try:
        io_mgr = GPIOManager("config/io_config.json")
        print(f"✓ GPIO Manager (mode: {io_mgr.simulation_mode and 'simulation' or 'hardware'})")
    except Exception as e:
        print(f"✗ GPIO Manager failed - {e}")
        return False
    
    return True


def main():
    print("=" * 60)
    print("  Pi Ladder Logic - Installation Test")
    print("=" * 60)
    print()
    
    tests = [
        ("Module Imports", test_imports),
        ("Tag Database", test_tag_database),
        ("Instructions", test_instructions),
        ("Runtime", test_runtime),
        ("GPIO Manager", test_gpio_manager),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"\n✗ {name} FAILED")
        except Exception as e:
            failed += 1
            print(f"\n✗ {name} FAILED with exception:")
            print(f"  {e}")
    
    print()
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✓ All tests passed! Pi Ladder Logic is ready to use.")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
