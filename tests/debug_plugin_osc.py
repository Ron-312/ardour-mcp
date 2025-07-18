#!/usr/bin/env python3
"""
Debug Plugin OSC Communication

This test helps us understand what OSC messages Ardour sends back
when we request plugin lists. Run this to see what we're missing!
"""

import requests
import time
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:8000"

def test_single_track_plugin_discovery():
    """Test plugin discovery for a single track with detailed logging"""
    print("[DEBUG] Single Track Plugin Discovery")
    print("=" * 60)
    print("This test will show exactly what OSC messages are received!")
    print()
    
    track_to_test = 1  # Test track 1 (which should have plugins)
    
    print(f"[TESTING] Plugin discovery for track {track_to_test}")
    print("Watch the server logs carefully for OSC messages!")
    print()
    
    try:
        print(f"[REQUEST] Sending request to: GET /plugins/track/{track_to_test}/plugins")
        
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/plugins/track/{track_to_test}/plugins", timeout=15)
        elapsed = time.time() - start_time
        
        print(f"[TIMING] Request completed in {elapsed:.1f}s")
        print(f"[STATUS] Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            plugins = result.get('plugins', [])
            print(f"[SUCCESS] API Response successful!")
            print(f"   Track: {result.get('track', 'unknown')}")
            print(f"   Plugin count: {result.get('count', 0)}")
            print(f"   Plugins found: {len(plugins)}")
            
            if plugins:
                print("[PLUGINS] Found plugins:")
                for i, plugin in enumerate(plugins):
                    track_id = plugin.get('track_id', 'unknown')
                    print(f"   {i+1}. {plugin.get('name', 'Unknown')} (ID: {plugin.get('id', '?')}, Track: {track_id}, Active: {plugin.get('active', '?')})")
            else:
                print("[ERROR] No plugins found - this is the problem we're debugging!")
                
        else:
            print(f"[ERROR] API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"[EXCEPTION] Request failed: {e}")
        
    print()
    print("[DEBUG] WHAT TO LOOK FOR IN SERVER LOGS:")
    print("1. Lines starting with '[PLUGIN OSC MESSAGE]'")
    print("2. Lines showing 'Sending OSC: /select/strip...'")
    print("3. Lines showing '[PLUGIN OSC MESSAGE]:' or '[STRIP OSC MESSAGE]:'")
    print("4. Lines showing 'Received OSC during discovery:'")
    print("5. Final result: 'Found X plugins' or 'No plugins found'")
    print()

def test_specific_plugin_discovery():
    """Test the new specific plugin discovery functionality"""
    print("[DEBUG] Specific Plugin Discovery")
    print("=" * 60)
    
    track_id = 1
    plugin_id = 0
    
    print(f"[TESTING] Specific plugin discovery: Track {track_id}, Plugin {plugin_id}")
    print("This tests the new discover_specific_plugin functionality")
    print()
    
    try:
        # We don't have an API endpoint for this yet, so let's test the discovery scan
        print(f"[REQUEST] Using comprehensive scan to find specific plugin...")
        
        response = requests.get(f"{BASE_URL}/plugins/discovery/scan", timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            print(f"[SUCCESS] Scan completed!")
            print(f"   Total tracks: {result.get('total_tracks', 0)}")
            print(f"   Total plugins: {result.get('total_plugins', 0)}")
            
            tracks = result.get('tracks', {})
            track_key = str(track_id)
            
            if track_key in tracks:
                track_plugins = tracks[track_key]
                print(f"[TRACK] Track {track_id} has {len(track_plugins)} plugins:")
                
                for plugin in track_plugins:
                    print(f"   - Plugin {plugin.get('id', '?')}: {plugin.get('name', 'Unknown')} ({plugin.get('type', 'unknown')}) [{'Active' if plugin.get('active') else 'Bypassed'}]")
                    
                if len(track_plugins) > plugin_id:
                    target_plugin = track_plugins[plugin_id]
                    print(f"[TARGET] Target plugin found: {target_plugin.get('name', 'Unknown')}")
                else:
                    print(f"[ERROR] Plugin {plugin_id} not found on track {track_id}")
            else:
                print(f"[ERROR] Track {track_id} not found in scan results")
                print(f"   Available tracks: {list(tracks.keys())}")
                
        else:
            print(f"[ERROR] Scan failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"[EXCEPTION] Scan failed: {e}")

def test_osc_message_capture():
    """Test that captures and displays OSC messages during discovery"""
    print("[DEBUG] OSC Message Capture")
    print("=" * 60)
    print("This test triggers discovery and shows what OSC responses we get")
    print()
    
    tracks_to_test = [0, 1, 2]  # Test tracks 0, 1, 2 (Ardour tracks 1, 2, 3)
    
    for track_idx in tracks_to_test:
        print(f"[TESTING] Track {track_idx} (Ardour track {track_idx + 1})...")
        
        try:
            # Small delay between requests
            time.sleep(1)
            
            response = requests.get(f"{BASE_URL}/plugins/track/{track_idx + 1}/plugins", timeout=8)
            
            if response.status_code == 200:
                result = response.json()
                count = result.get('count', 0)
                if count > 0:
                    print(f"   [SUCCESS] Found {count} plugins")
                else:
                    print(f"   [ERROR] No plugins found")
            else:
                print(f"   [ERROR] Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"   [EXCEPTION] Error: {e}")
            
    print()
    print("[INSTRUCTIONS] Next steps:")
    print("1. Check the server logs for OSC messages during the test above")
    print("2. Look for patterns in the OSC addresses Ardour sends")
    print("3. Note the format of plugin data in responses")
    print("4. We need to add handlers for any unrecognized OSC addresses")

def main():
    """Run all debug tests"""
    print("[TOOL] Plugin Discovery OSC Debug Tool")
    print("=" * 70)
    print("This tool helps debug why plugin discovery isn't finding plugins.")
    print("Make sure:")
    print("1. Ardour is running with plugins on tracks 1-3")
    print("2. MCP server is running") 
    print("3. Watch server logs during this test!")
    print()
    print("[AUTO] Starting debug tests automatically...")
    print()
    
    # Test 1: Single track discovery with detailed logging
    test_single_track_plugin_discovery()
    
    print("\n" + "="*70)
    print("[NEXT] Running comprehensive scan test...")
    print()
    
    # Test 2: Specific plugin discovery
    test_specific_plugin_discovery()
    
    print("\n" + "="*70)
    print("[NEXT] Running OSC message capture test...")
    print()
    
    # Test 3: OSC message capture
    test_osc_message_capture()
    
    print("\n" + "="*70)
    print("[COMPLETE] DEBUG TEST COMPLETE!")
    print()
    print("[NEXT STEPS]:")
    print("1. Review server logs for OSC messages")
    print("2. Identify what Ardour sends for plugin lists")
    print("3. Add missing OSC handlers for those messages")
    print("4. Test again to see if plugins are discovered")
    print()
    print("[LOGS] Key things to look for in logs:")
    print("   - OSC messages with 'plugin' in the address")
    print("   - OSC messages with 'strip' in the address") 
    print("   - Messages received during the 5-second discovery window")
    print("   - Any unknown OSC addresses that need handlers")

if __name__ == "__main__":
    main()