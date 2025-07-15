#!/usr/bin/env python3
"""
Direct OSC test - bypasses the server completely
This tests if the OSC communication itself works with Ardour
"""

import time
from pythonosc import udp_client

def test_direct_osc():
    """Test OSC communication directly to Ardour"""
    print("🎵 Direct OSC Communication Test")
    print("This bypasses the server completely")
    print("=" * 50)
    
    # Create direct OSC client
    try:
        client = udp_client.SimpleUDPClient("127.0.0.1", 3819)
        print("✅ OSC client created successfully")
    except Exception as e:
        print(f"❌ Failed to create OSC client: {e}")
        return
    
    # Test commands according to Ardour manual
    test_commands = [
        ("/transport_play", 1, "Start playback"),
        ("/transport_stop", 1, "Stop playback"), 
        ("/goto_start", 1, "Go to start"),
        ("/toggle_roll", 1, "Toggle play/stop"),
        ("/loop_toggle", 1, "Toggle loop mode"),
        ("/add_marker", 1, "Add marker"),
        ("/strip/0/mute", 1, "Mute track 1"),
        ("/strip/0/mute", 0, "Unmute track 1"),
        ("/strip/0/solo", 1, "Solo track 1"),
        ("/strip/0/solo", 0, "Unsolo track 1"),
        ("/strip/0/gain", -6.0, "Set track 1 gain to -6dB"),
        ("/strip/0/fader", 0.75, "Set track 1 fader to 75%"),
        ("/strip/0/pan_stereo_position", -0.5, "Pan track 1 left"),
        ("/strip/0/recenable", 1, "Enable recording on track 1"),
        ("/strip/0/recenable", 0, "Disable recording on track 1"),
        ("/strip/list", 1, "List all tracks"),
    ]
    
    print(f"\n🔍 Testing {len(test_commands)} OSC commands...")
    print("Watch Ardour for responses!")
    print()
    
    for address, value, description in test_commands:
        print(f"📡 {description}")
        print(f"   Sending: {address} {value}")
        
        try:
            client.send_message(address, value)
            print(f"   ✅ Sent successfully")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        time.sleep(1)  # Wait between commands
        print()
    
    # Test session commands (menu actions)
    print("🎛️ Testing Session Commands (Menu Actions)")
    print("-" * 30)
    
    session_commands = [
        ("/access_action", "Main/Save", "Save session"),
        ("/access_action", "Main/AddTrackBus", "Open Add Track dialog"),
        ("/access_action", "Editor/undo", "Undo last action"),
        ("/access_action", "Editor/redo", "Redo last action"),
    ]
    
    for address, action, description in session_commands:
        print(f"📡 {description}")
        print(f"   Sending: {address} \"{action}\"")
        
        try:
            client.send_message(address, action)
            print(f"   ✅ Sent successfully")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        time.sleep(2)  # Wait longer for menu actions
        print()

def test_track_naming():
    """Test track naming specifically"""
    print("🏷️ Direct Track Naming Test")
    print("=" * 30)
    
    try:
        client = udp_client.SimpleUDPClient("127.0.0.1", 3819)
        
        track_names = [
            (0, "Lead Vocals"),
            (1, "Bass Guitar"), 
            (2, "Drums"),
            (3, "Guitar Solo")
        ]
        
        for track_index, name in track_names:
            print(f"Setting track {track_index + 1} name to '{name}'")
            print(f"   OSC: /strip/{track_index}/name \"{name}\"")
            
            try:
                client.send_message(f"/strip/{track_index}/name", name)
                print(f"   ✅ Sent successfully")
            except Exception as e:
                print(f"   ❌ Failed: {e}")
            
            time.sleep(0.5)
            print()
            
    except Exception as e:
        print(f"❌ Failed to create OSC client: {e}")

def main():
    """Run direct OSC tests"""
    print("🎯 This test bypasses the broken server completely!")
    print("🎯 If these work, the issue is 100% with the server")
    print("🎯 If these don't work, the issue is with Ardour OSC setup")
    print()
    
    test_direct_osc()
    test_track_naming()
    
    print("=" * 50)
    print("🎯 DIRECT OSC TEST COMPLETE")
    print()
    print("🔍 Check Ardour to see if:")
    print("  - Transport moved (play/stop/goto start)")
    print("  - Track 1 mute/solo buttons changed")
    print("  - Track 1 fader/gain changed")
    print("  - Track names changed in mixer")
    print("  - Add Track dialog opened")
    print("  - Markers were added")
    print("  - Loop mode toggled")
    print()
    print("If these worked:")
    print("  ✅ OSC setup is correct")
    print("  ❌ Server needs restart to load new code")
    print()
    print("If these didn't work:")
    print("  ❌ Check Ardour OSC settings")
    print("  ❌ Check Window > Log for OSC messages")

if __name__ == "__main__":
    main()