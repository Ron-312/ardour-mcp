#!/usr/bin/env python3
"""
Test script to verify OSC connection to Ardour
Run this to check if Ardour is receiving OSC messages correctly
"""

import time
from pythonosc import udp_client

def test_ardour_connection():
    """Test direct OSC connection to Ardour"""
    print("🎵 Testing direct OSC connection to Ardour...")
    print("📋 Prerequisites:")
    print("  - Ardour is running with OSC enabled on port 3819") 
    print("  - OSC Debug mode enabled: Preferences > Control Surfaces > OSC > Debug = On")
    print("  - Session loaded in Ardour with at least one track")
    print()
    
    try:
        # Create OSC client
        client = udp_client.SimpleUDPClient("127.0.0.1", 3819)
        
        print("📡 Testing connection with query...")
        client.send_message("/strip/list", 1)
        time.sleep(0.5)
        
        print("▶️  Sending transport_play message...")
        client.send_message("/transport_play", 1)
        time.sleep(1)
        
        print("⏹️  Sending transport_stop message...")
        client.send_message("/transport_stop", 1) 
        time.sleep(1)
        
        print("🎚️  Sending test fader message...")
        client.send_message("/strip/1/gain", -10.0)
        time.sleep(0.5)
        
        print("🔄 Testing toggle_roll...")
        client.send_message("/toggle_roll", 1)
        time.sleep(1)
        client.send_message("/toggle_roll", 1)
        time.sleep(0.5)
        
        print("🏠 Testing goto_start...")
        client.send_message("/goto_start", 1)
        time.sleep(0.5)
        
        print()
        print("✅ OSC messages sent successfully!")
        print("🔍 Check Ardour's Window > Log for entries like:")
        print("   OSC: /transport_play")
        print("   OSC: /transport_stop") 
        print("   OSC: /strip/1/gain f:-10.0")
        print("   OSC: /toggle_roll")
        print("   OSC: /goto_start")
        print()
        print("🎯 Expected behavior:")
        print("  ✓ Playhead should move when transport_play is sent")
        print("  ✓ Transport should stop when transport_stop is sent")
        print("  ✓ Track 1 gain should change with /strip/1/gain")
        print()
        print("❌ If you don't see log entries, check:")
        print("  - Ardour OSC is enabled and set to port 3819")
        print("  - Debug mode is enabled in OSC settings")  
        print("  - No firewall is blocking UDP port 3819")
        print("  - Ardour session is loaded (not just Ardour running)")
        print("  - OSC surface is 'enabled' in Control Surfaces")
        
    except Exception as e:
        print(f"❌ Error sending OSC messages: {e}")
        print("Check that python-osc is installed: pip install python-osc")

if __name__ == "__main__":
    test_ardour_connection()