#!/usr/bin/env python3
"""
Debug script to find out what strips exist in Ardour
"""

import time
from pythonosc import udp_client

def debug_strips():
    """Test different strip numbers to see which ones exist"""
    print("🔍 STRIP DEBUGGING - Finding what strips exist")
    print("=" * 60)
    
    try:
        client = udp_client.SimpleUDPClient("127.0.0.1", 3819)
        print("✅ Connected to Ardour OSC")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    print("\n📡 Step 1: Request strip list information...")
    
    # Try different ways to get strip info
    info_commands = [
        "/strip/list",
        "/mixer/strips", 
        "/session_name",
        "/route/count",
    ]
    
    for cmd in info_commands:
        print(f"   Sending: {cmd}")
        try:
            client.send_message(cmd, 1)
        except Exception as e:
            print(f"   ❌ Error: {e}")
        time.sleep(0.5)
    
    print("\n⚠️  Check Ardour Window > Log for responses!")
    print("Look for any output from the commands above")
    print("\nWaiting 5 seconds for responses...")
    time.sleep(5)
    
    print("\n📡 Step 2: Testing different strip numbers...")
    print("We'll test strips 0-9 to see which ones exist")
    
    # Test strip numbers 0-9 with a simple command
    for i in range(10):
        print(f"Testing strip {i}...")
        try:
            # Use a read-only command (get mute state)
            client.send_message(f"/strip/{i}/mute", None)
            print(f"   📤 Sent command to strip {i}")
        except Exception as e:
            print(f"   ❌ Error sending to strip {i}: {e}")
        time.sleep(0.3)
    
    print("\n🔍 Step 3: Check Ardour logs now!")
    print("Look for:")
    print("  - Any strip information responses")
    print("  - 'No such strip' warnings")
    print("  - Which strip numbers DON'T give warnings")
    
    print("\n📋 Step 4: Session information...")
    
    # Get some basic session info
    session_commands = [
        ("/engine/transport_rolling", "Transport status"),
        ("/session_frame_rate", "Frame rate"),
        ("/session_timecode_format", "Timecode format"),
    ]
    
    for cmd, desc in session_commands:
        print(f"   {desc}: {cmd}")
        try:
            client.send_message(cmd, 1)
        except Exception as e:
            print(f"   ❌ Error: {e}")
        time.sleep(0.3)

def check_session_tracks():
    """Try to determine how many tracks exist"""
    print(f"\n🎛️ TRACK COUNT INVESTIGATION")
    print("=" * 40)
    
    try:
        client = udp_client.SimpleUDPClient("127.0.0.1", 3819)
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    # Try using select commands (these might work differently)
    print("Testing /select/ commands...")
    
    select_commands = [
        "/select/strip_type",
        "/select/n_strips", 
        "/select/track_count",
    ]
    
    for cmd in select_commands:
        print(f"   Trying: {cmd}")
        try:
            client.send_message(cmd, 1)
        except Exception as e:
            print(f"   ❌ Error: {e}")
        time.sleep(0.5)
    
    print(f"\nTesting /select/strip with different numbers...")
    # Test selecting different strips
    for i in range(5):
        print(f"   Selecting strip {i}: /select/strip {i}")
        try:
            client.send_message("/select/strip", i)
            time.sleep(0.2)
            # Try to get info about selected strip
            client.send_message("/select/name", 1)
        except Exception as e:
            print(f"   ❌ Error: {e}")
        time.sleep(0.3)

def main():
    print("🎯 ARDOUR STRIP DEBUGGING TOOL")
    print("This will help us figure out why 'No such strip' errors occur")
    print("=" * 70)
    
    debug_strips()
    check_session_tracks()
    
    print("\n" + "=" * 70)
    print("🎯 DEBUGGING COMPLETE")
    print("\n📋 WHAT TO LOOK FOR IN ARDOUR LOGS:")
    print("1. Any responses to /strip/list or /mixer/strips")
    print("2. Which strip numbers (0-9) DON'T show 'No such strip'")
    print("3. Any track count or route count information")
    print("4. Responses to /select/ commands")
    
    print("\n💡 NEXT STEPS:")
    print("1. Check Ardour Window > Log")
    print("2. Tell me which strip numbers work (no warnings)")
    print("3. If ALL strips show warnings, you need to add tracks:")
    print("   - In Ardour: Track > Add Track/Bus...")
    print("   - Add 2-3 Audio Tracks")
    print("   - Run this test again")

if __name__ == "__main__":
    main()