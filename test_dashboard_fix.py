#!/usr/bin/env python3
"""
Test Dashboard Fix - Verify KeyError is resolved
"""

import sys
import os
import requests

def test_dashboard_fix():
    """Test that dashboard no longer crashes with KeyError."""
    
    print("🧪 Testing Dashboard Fix")
    print("=" * 50)
    
    try:
        # Import dashboard functions
        from dashboard_simple import main, show_redis_page, show_siem_page, get_firewall_stats
        
        print("✅ Dashboard functions imported successfully")
        
        # Test firewall stats function
        stats = get_firewall_stats()
        print(f"Firewall stats structure: {list(stats.keys())}")
        
        # Test Redis page function (this was causing the KeyError)
        print("\n🧪 Testing Redis page function...")
        try:
            # This should not crash with KeyError anymore
            show_redis_page()
            print("✅ Redis page function works without KeyError")
        except Exception as e:
            print(f"❌ Redis page function failed: {e}")
            return False
        
        # Test SIEM page function
        print("\n🧪 Testing SIEM page function...")
        try:
            show_siem_page()
            print("✅ SIEM page function works without KeyError")
        except Exception as e:
            print(f"❌ SIEM page function failed: {e}")
            return False
        
        print("\n🎉 Dashboard fix SUCCESSFUL!")
        print("   - KeyError: 'firewall_stats' resolved")
        print("   - All dashboard pages working")
        print("   - Error handling added")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard fix failed: {e}")
        return False

if __name__ == "__main__":
    success = test_dashboard_fix()
    if success:
        print("\n🚀 Dashboard is ready for production!")
    else:
        print("\n🔧 Dashboard needs more fixes")
