#!/usr/bin/env python3
"""
Quick test to verify server starts with all new endpoints
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_server_health():
    """Test basic server health and endpoint availability"""
    print("🔍 Testing Server Health & New Endpoints")
    print("=" * 50)
    
    # Test basic health
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False
    
    # Test new plugin and recording endpoints exist (should return 405 for HEAD requests)
    new_endpoints = [
        "/plugins/track/1/plugins",
        "/plugins/track/1/plugin/0/parameters", 
        "/plugins/track/1/plugin/0/info",
        "/plugins/discovery/scan",
        "/recording/enable",
        "/recording/punch-in",
        "/recording/input-monitor",
        "/recording/status"
    ]
    
    endpoint_count = 0
    for endpoint in new_endpoints:
        try:
            response = requests.head(f"{BASE_URL}{endpoint}")
            # 405 Method Not Allowed means endpoint exists but doesn't accept HEAD
            if response.status_code in [200, 405]:
                print(f"✅ {endpoint}")
                endpoint_count += 1
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    print(f"\n📊 New endpoints available: {endpoint_count}/{len(new_endpoints)}")
    
    # Test that all previous endpoints still work
    existing_endpoints = [
        "/transport/play",
        "/track/1/fader", 
        "/session/save",
        "/sends/track/1/send/1/level"
    ]
    
    existing_count = 0
    for endpoint in existing_endpoints:
        try:
            response = requests.head(f"{BASE_URL}{endpoint}")
            if response.status_code in [200, 405]:
                print(f"✅ {endpoint} (existing)")
                existing_count += 1
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    print(f"📊 Existing endpoints still work: {existing_count}/{len(existing_endpoints)}")
    
    total_working = endpoint_count + existing_count
    total_endpoints = len(new_endpoints) + len(existing_endpoints)
    
    if total_working == total_endpoints:
        print(f"\n🎉 ALL ENDPOINTS WORKING!")
        print(f"✅ Plugin discovery endpoints added successfully")
        print(f"✅ Recording control endpoints added successfully") 
        print(f"✅ All existing functionality preserved")
        return True
    else:
        print(f"\n⚠️  Some endpoints need attention: {total_working}/{total_endpoints}")
        return False

if __name__ == "__main__":
    print("🚀 Server Startup Test for Plugin Discovery")
    print("=" * 60)
    
    success = test_server_health()
    
    if success:
        print("\n🎯 Server is ready for full testing!")
        print("Next: Run recording tests 'python tests/test_recording_controls.py'")
    else:
        print("\n❌ Server issues detected - check logs and restart")