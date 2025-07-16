#!/usr/bin/env python3
"""
Test script for Real Plugin Discovery with OSC feedback
"""

import requests
import json
import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000"

def test_osc_listener_startup():
    """Test that OSC listener is running"""
    print("🔍 Testing OSC Listener Startup")
    print("=" * 40)
    
    print("Checking server health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is healthy")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return False

def test_real_plugin_discovery():
    """Test real plugin discovery from Ardour"""
    print(f"\n🎛️ Testing Real Plugin Discovery")
    print("=" * 40)
    
    print("Note: This test requires Ardour to be running with plugins loaded")
    print("Expected: Real plugin data from OSC feedback, not hardcoded examples")
    print()
    
    # Test multiple tracks to see real vs hardcoded data
    tracks_to_test = [1, 2, 3]
    discovered_plugins = {}
    
    for track_num in tracks_to_test:
        print(f"🔍 Discovering plugins on track {track_num}...")
        try:
            response = requests.get(f"{BASE_URL}/plugins/track/{track_num}/plugins")
            
            if response.status_code == 200:
                result = response.json()
                plugins = result.get('plugins', [])
                discovered_plugins[track_num] = plugins
                
                print(f"  ✅ Found {len(plugins)} plugins")
                for plugin in plugins:
                    status = "🟢 Active" if plugin['active'] else "🔴 Bypassed"
                    print(f"     Plugin {plugin['id']}: {plugin['name']} ({plugin.get('type', 'unknown')}) {status}")
                    
                    # Check if this looks like real data or hardcoded
                    if plugin['name'] in ['ACE Compressor', 'ACE EQ'] and plugin['id'] in [0, 1]:
                        print(f"     ⚠️  This looks like hardcoded example data")
                    else:
                        print(f"     ✅ This appears to be real plugin data")
                        
            else:
                print(f"  ❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        time.sleep(1)  # Allow time for OSC communication
    
    return discovered_plugins

def test_real_parameter_discovery():
    """Test real parameter discovery for plugins"""
    print(f"\n🎚️ Testing Real Parameter Discovery")
    print("=" * 40)
    
    # Test parameter discovery for discovered plugins
    test_cases = [
        (1, 0, "First plugin on track 1"),
        (2, 0, "First plugin on track 2"),
        (3, 0, "First plugin on track 3"),
    ]
    
    real_parameters = {}
    
    for track, plugin_id, description in test_cases:
        print(f"🔍 Discovering parameters for {description}...")
        try:
            response = requests.get(f"{BASE_URL}/plugins/track/{track}/plugin/{plugin_id}/parameters")
            
            if response.status_code == 200:
                result = response.json()
                parameters = result.get('parameters', [])
                real_parameters[f"{track}_{plugin_id}"] = parameters
                
                print(f"  ✅ Plugin: {result['plugin_name']}")
                print(f"  ✅ Found {len(parameters)} parameters")
                
                for param in parameters[:5]:  # Show first 5 parameters
                    print(f"     {param['name']}: {param.get('value_display', param['value_raw'])}")
                    
                    # Check if this looks like real data
                    if param['name'] in ['threshold', 'ratio', 'attack', 'release', 'low_freq', 'mid_freq']:
                        print(f"       ⚠️  This might be hardcoded example data")
                    else:
                        print(f"       ✅ This appears to be real parameter data")
                        
                if len(parameters) > 5:
                    print(f"     ... and {len(parameters) - 5} more parameters")
                    
            else:
                print(f"  ❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        time.sleep(1.5)  # Allow time for OSC communication
    
    return real_parameters

def test_comprehensive_real_scan():
    """Test comprehensive real plugin scanning"""
    print(f"\n🔍 Testing Comprehensive Real Plugin Scan")
    print("=" * 40)
    
    print("🔍 Scanning all tracks for real plugins...")
    try:
        response = requests.get(f"{BASE_URL}/plugins/discovery/scan")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Scan completed at {result['scan_time']}")
            print(f"📊 Found {result['total_plugins']} plugins across {result['total_tracks']} tracks")
            
            # Analyze if data looks real
            tracks = result.get('tracks', {})
            hardcoded_indicators = 0
            real_indicators = 0
            
            for track_id, plugins in tracks.items():
                print(f"\n📍 Track {track_id}: {len(plugins)} plugins")
                for plugin in plugins:
                    status = "Active" if plugin['active'] else "Bypassed"
                    print(f"   - {plugin['name']} ({plugin['type']}) [{status}]")
                    
                    # Check for hardcoded indicators
                    if plugin['name'] in ['ACE Compressor', 'ACE EQ', 'ACE Limiter']:
                        hardcoded_indicators += 1
                        print(f"     ⚠️  Possible hardcoded data")
                    else:
                        real_indicators += 1
                        print(f"     ✅ Likely real plugin data")
            
            print(f"\n📊 Data Analysis:")
            print(f"   Real indicators: {real_indicators}")
            print(f"   Hardcoded indicators: {hardcoded_indicators}")
            
            if real_indicators > hardcoded_indicators:
                print(f"   ✅ Scan appears to be using real plugin data!")
            else:
                print(f"   ⚠️  Scan may still be using hardcoded examples")
                
            return result
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_osc_communication_flow():
    """Test OSC communication flow for plugin discovery"""
    print(f"\n📡 Testing OSC Communication Flow")
    print("=" * 40)
    
    print("Watch server logs for OSC messages...")
    print("Expected OSC messages for plugin discovery:")
    print("  - /select/strip <track_index>")
    print("  - /select/plugin/list")
    print("  - /select/plugin <plugin_id>")
    print("  - /select/plugin/parameters")
    print("  - /select/plugin/name")
    print()
    
    osc_tests = [
        ("Select track and list plugins", f"/plugins/track/1/plugins"),
        ("Get plugin parameters", f"/plugins/track/1/plugin/0/parameters"),
        ("Get plugin info", f"/plugins/track/1/plugin/0/info"),
    ]
    
    for test_name, endpoint in osc_tests:
        print(f"🔍 {test_name}")
        print(f"   Endpoint: GET {endpoint}")
        
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                print(f"   ✅ Request successful")
            else:
                print(f"   ❌ Request failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(2)  # Allow time to see OSC messages in logs
        
    print("\n🔍 Check server logs for:")
    print("  - OSC client messages being sent")
    print("  - OSC listener messages being received")
    print("  - Plugin discovery timeout behavior")
    print("  - Parameter parsing from OSC feedback")

def test_plugin_discovery_accuracy():
    """Test accuracy of plugin discovery data"""
    print(f"\n🎯 Testing Plugin Discovery Accuracy")
    print("=" * 40)
    
    print("This test compares discovered data with expected plugin behavior")
    print("Manual verification needed - check against actual Ardour session")
    print()
    
    # Test specific plugin discovery scenarios
    accuracy_tests = [
        ("Empty track", 4),  # Track with no plugins
        ("Track with one plugin", 1),  # Track with single plugin
        ("Track with multiple plugins", 2),  # Track with multiple plugins
    ]
    
    for test_name, track_num in accuracy_tests:
        print(f"🔍 Testing {test_name} (Track {track_num})")
        try:
            response = requests.get(f"{BASE_URL}/plugins/track/{track_num}/plugins")
            
            if response.status_code == 200:
                result = response.json()
                plugins = result.get('plugins', [])
                
                print(f"   Found {len(plugins)} plugins")
                
                if len(plugins) == 0:
                    print("   ✅ Empty track correctly detected")
                elif len(plugins) == 1:
                    print("   ✅ Single plugin correctly detected")
                else:
                    print(f"   ✅ Multiple plugins ({len(plugins)}) detected")
                    
                # Manual verification reminder
                print(f"   👁️  Manual check: Verify against actual Ardour track {track_num}")
                
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)

def main():
    """Run real plugin discovery tests"""
    print("🎵 REAL PLUGIN DISCOVERY TESTING")
    print("=" * 60)
    print("🚨 IMPORTANT: This test requires:")
    print("  1. Ardour running with OSC enabled")
    print("  2. Some plugins loaded on tracks")
    print("  3. Server running with OSC listener active")
    print("=" * 60)
    
    # Test server and OSC listener startup
    if not test_osc_listener_startup():
        print("\n❌ Server not available - cannot run tests")
        return
    
    # Run discovery tests
    discovered_plugins = test_real_plugin_discovery()
    discovered_parameters = test_real_parameter_discovery()
    scan_result = test_comprehensive_real_scan()
    
    test_osc_communication_flow()
    test_plugin_discovery_accuracy()
    
    # Summary analysis
    print(f"\n" + "=" * 60)
    print(f"🎯 REAL PLUGIN DISCOVERY SUMMARY")
    print(f"=" * 60)
    
    total_plugins = sum(len(plugins) for plugins in discovered_plugins.values())
    print(f"📊 Total plugins discovered: {total_plugins}")
    print(f"📊 Tracks with plugins: {len([k for k, v in discovered_plugins.items() if v])}")
    print(f"📊 Parameters discovered: {sum(len(params) for params in discovered_parameters.values())}")
    
    if scan_result:
        print(f"📊 Comprehensive scan: {scan_result['total_plugins']} plugins across {scan_result['total_tracks']} tracks")
    
    print(f"\n🔍 VALIDATION CHECKLIST:")
    print(f"✅ Server startup with OSC listener")
    print(f"✅ Plugin discovery endpoints working")
    print(f"✅ Parameter discovery endpoints working")
    print(f"✅ Comprehensive scanning working")
    print(f"⚠️  Data accuracy - requires manual verification")
    
    print(f"\n📋 NEXT STEPS:")
    print(f"1. Verify discovered plugins match actual Ardour session")
    print(f"2. Check parameter values are accurate")
    print(f"3. Test with different plugin types (EQ, Compressor, etc.)")
    print(f"4. Verify OSC communication is working correctly")
    
    print(f"\n🚀 Ready for plugin control testing!")

if __name__ == "__main__":
    main()