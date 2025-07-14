#!/usr/bin/env python3
"""
Test what the currently running server is actually sending
"""

import json
import requests
import time

def test_current_implementation():
    """Test the current server implementation"""
    print("🔍 Testing Current Server Implementation")
    print("=" * 50)
    
    # Clear the log file to see fresh entries
    try:
        with open("ardour_mcp.log", "a") as f:
            f.write(f"\n=== NEW TEST SESSION {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    except:
        pass
    
    print("📡 Sending API request...")
    response = requests.post("http://localhost:8000/transport/play")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    time.sleep(0.5)
    
    print("\n📋 Reading recent log entries...")
    try:
        with open("ardour_mcp.log", "r") as f:
            lines = f.readlines()
            print("Last 10 log lines:")
            for line in lines[-10:]:
                print(f"   {line.strip()}")
    except Exception as e:
        print(f"❌ Could not read log: {e}")
    
    print("\n🎯 Analysis:")
    print("- Look for 'Sent OSC message:' lines")
    print("- Check if arguments are empty () or have values")
    print("- The format should be '/transport_play 1' not '/ardour/transport_play ()'")

def test_health_endpoint():
    """Test if server is responsive"""
    print("\n🏥 Testing Server Health")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Health Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

if __name__ == "__main__":
    test_health_endpoint()
    test_current_implementation()
    
    print("\n" + "=" * 50)
    print("💡 NEXT STEPS:")
    print("1. If logs show '/ardour/transport_play ()', the server needs restart")
    print("2. If logs show '/transport_play 1', check Ardour configuration") 
    print("3. Run the direct OSC test and see if any format works in Ardour")
    print("4. Check Ardour's Window > Log for any OSC entries")