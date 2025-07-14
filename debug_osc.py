#!/usr/bin/env python3
"""
Debug OSC communication - comprehensive test with multiple formats
"""

import time
import logging
from pythonosc import udp_client

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

def test_all_formats():
    """Test different OSC message formats for Ardour"""
    
    print("🔍 Debug: Testing all possible OSC transport formats...")
    client = udp_client.SimpleUDPClient("127.0.0.1", 3819)
    
    test_cases = [
        # Format 1: Basic commands without arguments
        ("/transport_play", None),
        ("/transport_stop", None),
        
        # Format 2: Commands with integer argument
        ("/transport_play", 1),
        ("/transport_stop", 1),
        
        # Format 3: Ardour prefix (older versions)
        ("/ardour/transport_play", None),
        ("/ardour/transport_stop", None),
        ("/ardour/transport_play", 1),
        ("/ardour/transport_stop", 1),
        
        # Format 4: Different argument types
        ("/transport_play", True),
        ("/transport_stop", True),
        ("/transport_play", 1.0),
        ("/transport_stop", 1.0),
        
        # Format 5: Alternative commands
        ("/toggle_roll", None),
        ("/toggle_roll", 1),
        ("/rec_enable_toggle", None),
        ("/rec_enable_toggle", 1),
    ]
    
    for i, (address, value) in enumerate(test_cases):
        print(f"\n🧪 Test {i+1}: {address} with value: {value}")
        try:
            if value is None:
                client.send_message(address)
                print(f"   ✅ Sent: {address} (no arguments)")
            else:
                client.send_message(address, value)
                print(f"   ✅ Sent: {address} {value}")
            time.sleep(0.5)
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print("\n🎯 Test Summary:")
    print("Check Ardour's Window > Log (with Debug=On) for any entries")
    print("If you see ANY log entries, note which format worked")
    print("If the playhead moves at any point, that format is correct")

if __name__ == "__main__":
    test_all_formats()