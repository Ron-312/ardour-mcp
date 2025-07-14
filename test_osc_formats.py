#!/usr/bin/env python3
"""
Test different OSC message formats to find what works with Ardour
This helps identify the correct format without restarting the server
"""

import time
import json
import requests
from pythonosc import udp_client

def test_direct_osc():
    """Test OSC messages directly (bypassing our server)"""
    print("🔍 Testing Direct OSC Communication to Ardour")
    print("=" * 50)
    
    client = udp_client.SimpleUDPClient("127.0.0.1", 3819)
    
    tests = [
        ("Current Format (no /ardour prefix)", "/transport_play", 1),
        ("Legacy Format (with /ardour prefix)", "/ardour/transport_play", 1),
        ("Manual Toggle", "/toggle_roll", 1),
        ("Goto Start", "/goto_start", 1),
        ("Stop", "/transport_stop", 1),
    ]
    
    for name, address, value in tests:
        print(f"\n📡 {name}: {address} {value}")
        try:
            client.send_message(address, value)
            print(f"   ✅ Sent successfully")
            time.sleep(1.5)  # Give time to see effect in Ardour
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print("\n🎯 Check Ardour now:")
    print("   - Did the playhead move?") 
    print("   - Any entries in Window > Log?")
    print("   - Which format worked?")

def test_api_endpoint():
    """Test our API endpoint to see what it's actually sending"""
    print("\n🌐 Testing API Endpoint")
    print("=" * 50)
    
    try:
        response = requests.post("http://localhost:8000/transport/play")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Check logs immediately after
        print("\n📋 Recent server logs:")
        with open("ardour_mcp.log", "r") as f:
            lines = f.readlines()
            for line in lines[-5:]:  # Last 5 lines
                if "OSC" in line or "transport" in line:
                    print(f"   {line.strip()}")
                    
    except Exception as e:
        print(f"❌ API test failed: {e}")

def test_network_connectivity():
    """Test if the network path to Ardour is working"""
    print("\n🔌 Testing Network Connectivity")
    print("=" * 50)
    
    import socket
    
    try:
        # Test UDP connectivity
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        
        # Send a test message
        test_message = b"/ping\x00\x00\x00,\x00\x00\x00"  # Simple OSC ping
        sock.sendto(test_message, ("127.0.0.1", 3819))
        
        print("✅ UDP packet sent to 127.0.0.1:3819")
        
        sock.close()
        
    except Exception as e:
        print(f"❌ Network test failed: {e}")
        print("   - Check if Ardour is running")
        print("   - Check if OSC is enabled on port 3819")
        print("   - Check firewall settings")

def main():
    print("🎵 Ardour OSC Debugging Tool")
    print("This will help identify why transport commands aren't working")
    print()
    
    # Test 1: Direct OSC (most reliable)
    test_direct_osc()
    
    # Test 2: Our API
    test_api_endpoint()
    
    # Test 3: Network connectivity
    test_network_connectivity()
    
    print("\n" + "=" * 50)
    print("🎯 TROUBLESHOOTING CHECKLIST:")
    print("1. Is Ardour running with a session loaded?")
    print("2. Is OSC enabled: Edit > Preferences > Control Surfaces > OSC?")
    print("3. Is OSC Debug enabled in the same menu?")
    print("4. Is the OSC port set to 3819?")
    print("5. Is the OSC control surface 'Enabled' (checkbox checked)?")
    print("6. Any entries in Ardour's Window > Log?")
    print("7. Did any test move the playhead?")

if __name__ == "__main__":
    main()