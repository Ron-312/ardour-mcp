#!/usr/bin/env python3
"""
Diagnostic script to check which version of the server is running
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def check_server_version():
    """Check if server is running old or new version"""
    print("🔍 Diagnosing Server Version")
    print("=" * 40)
    
    # Test old endpoints (should work)
    old_endpoints = [
        "/transport/play",
        "/transport/stop", 
        "/track/1/fader",
        "/track/1/mute"
    ]
    
    # Test new endpoints (should work if server restarted)
    new_endpoints = [
        "/transport/rewind",
        "/transport/toggle-loop",
        "/session/save",
        "/session/add-track-dialog"
    ]
    
    print("Testing OLD endpoints (should work):")
    old_working = 0
    for endpoint in old_endpoints:
        try:
            response = requests.head(f"{BASE_URL}{endpoint}")
            status = "✅" if response.status_code in [200, 405] else "❌"
            print(f"  {status} {endpoint} - {response.status_code}")
            if response.status_code in [200, 405]:
                old_working += 1
        except Exception as e:
            print(f"  ❌ {endpoint} - Error: {e}")
    
    print(f"\nTesting NEW endpoints (only work if server restarted):")
    new_working = 0
    for endpoint in new_endpoints:
        try:
            response = requests.head(f"{BASE_URL}{endpoint}")
            status = "✅" if response.status_code in [200, 405] else "❌"
            print(f"  {status} {endpoint} - {response.status_code}")
            if response.status_code in [200, 405]:
                new_working += 1
        except Exception as e:
            print(f"  ❌ {endpoint} - Error: {e}")
    
    print(f"\n📊 Results:")
    print(f"  Old endpoints working: {old_working}/{len(old_endpoints)}")
    print(f"  New endpoints working: {new_working}/{len(new_endpoints)}")
    
    if new_working == 0:
        print(f"\n🚨 DIAGNOSIS: Server is running OLD version")
        print(f"   - Need to restart server to load new Phase 2 features")
        print(f"   - New session and enhanced transport endpoints not available")
        return False
    else:
        print(f"\n✅ DIAGNOSIS: Server is running NEW version")
        return True

def check_osc_format():
    """Check if OSC format issue is fixed"""
    print(f"\n🔍 Testing OSC Format Fix")
    print("=" * 40)
    
    try:
        response = requests.post(f"{BASE_URL}/transport/play")
        if response.status_code == 200:
            result = response.json()
            osc_address = result.get('osc_address', 'NOT_FOUND')
            
            if osc_address == "/transport_play":
                print(f"✅ OSC format FIXED: {osc_address}")
                return True
            elif osc_address == "/ardour/transport_play":
                print(f"❌ OSC format still BROKEN: {osc_address}")
                print(f"   Expected: /transport_play")
                print(f"   Got: {osc_address}")
                return False
            else:
                print(f"❓ Unexpected OSC format: {osc_address}")
                return False
        else:
            print(f"❌ Can't test OSC format - transport endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing OSC format: {e}")
        return False

def check_osc_arguments():
    """Check server logs for OSC argument format"""
    print(f"\n🔍 Testing OSC Arguments")
    print("=" * 40)
    print("Watch the server logs when this runs...")
    print("Looking for: 'Sent OSC message: /transport_play 1'")
    print("NOT: 'Sent OSC message: /ardour/transport_play ()'")
    
    try:
        response = requests.post(f"{BASE_URL}/transport/play")
        if response.status_code == 200:
            print(f"✅ Play command sent - check server logs above")
            print(f"Should see: 'OSC Client connecting to...'")
            print(f"Should see: 'Sending OSC message: /transport_play with args: (1,)'")
        else:
            print(f"❌ Play command failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all diagnostic tests"""
    print("🎵 Ardour MCP Server Diagnostic Tool")
    print("=" * 50)
    
    server_updated = check_server_version()
    osc_fixed = check_osc_format()
    check_osc_arguments()
    
    print(f"\n" + "=" * 50)
    print(f"🎯 DIAGNOSTIC SUMMARY:")
    print(f"  Server has new endpoints: {'✅' if server_updated else '❌'}")
    print(f"  OSC format fixed: {'✅' if osc_fixed else '❌'}")
    
    if not server_updated:
        print(f"\n🔧 REQUIRED ACTIONS:")
        print(f"  1. Restart the FastAPI server to load new code")
        print(f"  2. Kill existing server process and restart")
        print(f"  3. Or use: uvicorn mcp_server.main:app --reload")
    
    if not osc_fixed:
        print(f"\n🔧 OSC FORMAT ISSUE:")
        print(f"  1. Server may still be running old code")
        print(f"  2. Check if OSC client changes were applied")

if __name__ == "__main__":
    main()