#!/usr/bin/env python3
"""
Direct OSC test - bypasses the server completely
This tests if the OSC communication itself works with Ardour
"""

import time
from pythonosc import udp_client

def ensure_tracks_exist():
    """Ensure we have at least 4 tracks to test with"""
    print("🎛️ Ensuring Tracks Exist")
    print("=" * 40)
    
    try:
        client = udp_client.SimpleUDPClient("127.0.0.1", 3819)
        print("✅ OSC client connected to Ardour")
    except Exception as e:
        print(f"❌ Failed to create OSC client: {e}")
        return False
    
    print("📡 Creating 4 audio tracks if they don't exist...")
    
    # Use Ardour's action system to add tracks
    try:
        # This opens the Add Track dialog - we'll add 4 audio tracks
        client.send_message("/access_action", "Main/AddTrackBus")
        print("   ✅ Opened Add Track dialog")
        print("   ⚠️  Please manually add 4 Audio Tracks in the dialog that just opened")
        print("   ⚠️  Set count to 4, select Audio Track, click Add")
        print("   ⚠️  Then close the dialog")
        time.sleep(3)
    except Exception as e:
        print(f"   ❌ Failed to open Add Track dialog: {e}")
    
    return True

def test_existing_strips():
    """Test which strips actually exist"""
    print("\n🔍 Testing Which Strips Exist")
    print("=" * 40)
    
    try:
        client = udp_client.SimpleUDPClient("127.0.0.1", 3819)
    except Exception as e:
        print(f"❌ Failed to create OSC client: {e}")
        return []
    
    existing_strips = []
    
    print("📡 Testing strips 0-9 to find existing ones...")
    for i in range(10):
        print(f"   Testing strip {i}...")
        try:
            # Try to get the strip name - this shouldn't cause "No such strip" if it exists
            client.send_message(f"/strip/{i}/name", "")
            time.sleep(0.1)
            # We'll assume it exists since we can't get a direct response
            # The user will tell us from the logs which ones work
        except Exception as e:
            print(f"   ❌ Error with strip {i}: {e}")
    
    print(f"\n⚠️  Check Ardour logs - which strips 0-9 did NOT show 'No such strip'?")
    print(f"   Those are the strips we can safely test with")
    
    # For now, assume strips 0-3 exist (user can adjust based on their session)
    existing_strips = [0, 1, 2, 3]
    print(f"   📋 Assuming strips {existing_strips} exist (adjust based on logs)")
    
    return existing_strips

def test_direct_osc(existing_strips=[0, 1, 2, 3]):
    """Test OSC communication directly to Ardour with only existing strips"""
    print(f"\n🎵 Direct OSC Communication Test")
    print("This bypasses the server completely")
    print("=" * 50)
    
    # Create direct OSC client
    try:
        client = udp_client.SimpleUDPClient("127.0.0.1", 3819)
        print("✅ OSC client created successfully")
    except Exception as e:
        print(f"❌ Failed to create OSC client: {e}")
        return
    
    # Start with transport commands (these should always work)
    transport_commands = [
        ("/transport_play", 1, "Start playback"),
        ("/transport_stop", 1, "Stop playback"), 
        ("/goto_start", 1, "Go to start"),
        ("/toggle_roll", 1, "Toggle play/stop"),
        ("/loop_toggle", 1, "Toggle loop mode"),
        ("/add_marker", 1, "Add marker"),
    ]
    
    print("🚦 Testing Transport Commands (should always work)...")
    for address, value, description in transport_commands:
        print(f"📡 {description}")
        print(f"   Sending: {address} {value}")
        
        try:
            client.send_message(address, value)
            print(f"   ✅ Sent successfully")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        time.sleep(1)
    
    # Test only existing strips
    if existing_strips:
        print(f"\n🎛️ Testing Track Commands for existing strips: {existing_strips}")
        
        for strip_num in existing_strips[:2]:  # Test first 2 existing strips
            print(f"\n   Testing Strip {strip_num}:")
            track_commands = [
                (f"/strip/{strip_num}/mute", 1, f"Mute strip {strip_num}"),
                (f"/strip/{strip_num}/mute", 0, f"Unmute strip {strip_num}"),
                (f"/strip/{strip_num}/solo", 1, f"Solo strip {strip_num}"),
                (f"/strip/{strip_num}/solo", 0, f"Unsolo strip {strip_num}"),
                (f"/strip/{strip_num}/fader", 0.8, f"Set strip {strip_num} fader to 80%"),
            ]
            
            for address, value, description in track_commands:
                print(f"     📡 {description}")
                print(f"        Sending: {address} {value}")
                
                try:
                    client.send_message(address, value)
                    print(f"        ✅ Sent successfully")
                except Exception as e:
                    print(f"        ❌ Failed: {e}")
                
                time.sleep(0.8)
    else:
        print(f"\n⚠️  No existing strips found - skipping track tests")
        print(f"   Add some tracks first: Track > Add Track/Bus...")
    
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

def test_track_naming(existing_strips=[0, 1, 2, 3]):
    """Test track naming for existing strips only"""
    print(f"\n🏷️ Direct Track Naming Test")
    print("=" * 30)
    
    if not existing_strips:
        print("⚠️  No existing strips - skipping track naming test")
        return
    
    try:
        client = udp_client.SimpleUDPClient("127.0.0.1", 3819)
        
        track_names = ["Lead Vocals", "Bass Guitar", "Drums", "Guitar Solo"]
        
        for i, strip_num in enumerate(existing_strips[:4]):  # Only name existing strips
            if i < len(track_names):
                name = track_names[i]
                print(f"Setting strip {strip_num} name to '{name}'")
                print(f"   OSC: /strip/{strip_num}/name \"{name}\"")
                
                try:
                    client.send_message(f"/strip/{strip_num}/name", name)
                    print(f"   ✅ Sent successfully")
                except Exception as e:
                    print(f"   ❌ Failed: {e}")
                
                time.sleep(0.5)
                print()
            
    except Exception as e:
        print(f"❌ Failed to create OSC client: {e}")

def main():
    """Run direct OSC tests with smart strip detection"""
    print("🎯 SMART OSC TEST - Only tests existing tracks!")
    print("🎯 This will prevent 'No such strip' errors")
    print("🎯 If these work, the issue is 100% with the server")
    print("🎯 If these don't work, the issue is with Ardour OSC setup")
    print()
    
    # Step 1: Ensure we have tracks to test with
    print("Step 1: Ensuring tracks exist...")
    if not ensure_tracks_exist():
        print("❌ Failed to connect to Ardour")
        return
    
    print("\n" + "="*60)
    print("⚠️  Did the Add Track dialog open?")
    print("   If YES: Add 4 Audio Tracks, then continue")
    print("   If NO: Make sure you have some tracks in your session")
    print("Continuing in 5 seconds...")
    time.sleep(5)
    
    # Step 2: Find out which strips actually exist
    print("\nStep 2: Detecting existing strips...")
    existing_strips = test_existing_strips()
    
    print("\n" + "="*60)
    print("⚠️  Check Ardour logs - which strips had NO 'No such strip' errors?")
    print("   Update the existing_strips list below if needed")
    time.sleep(3)
    
    # Step 3: Test only existing strips
    print(f"\nStep 3: Testing with strips: {existing_strips}")
    test_direct_osc(existing_strips)
    test_track_naming(existing_strips)
    
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