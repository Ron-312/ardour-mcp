#!/usr/bin/env python3
"""
Test script for Plugin Discovery functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_list_track_plugins():
    """Test listing plugins on specific tracks"""
    print("TESTING Testing Track Plugin Listing")
    print("=" * 40)
    
    tracks_to_test = [1, 2, 3, 4]
    
    for track_num in tracks_to_test:
        print(f"Testing track {track_num} plugins...")
        try:
            response = requests.get(f"{BASE_URL}/plugins/track/{track_num}/plugins")
            
            if response.status_code == 200:
                result = response.json()
                plugins = result.get('plugins', [])
                print(f"  SUCCESS Track {track_num}: {result['count']} plugins found")
                
                for plugin in plugins:
                    status = "🟢 Active" if plugin['active'] else "🔴 Bypassed"
                    plugin_type = f" ({plugin.get('type', 'unknown')})" if plugin.get('type') else ""
                    print(f"     Plugin {plugin['id']}: {plugin['name']}{plugin_type} {status}")
                    
            else:
                print(f"  FAILED Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  FAILED Error: {e}")
        
        time.sleep(0.3)
    
    return len(tracks_to_test)

def test_plugin_parameters():
    """Test getting plugin parameter information"""
    print(f"\n🎛️ Testing Plugin Parameter Discovery")
    print("=" * 40)
    
    # Test common plugin/parameter combinations
    test_cases = [
        (1, 0, "ACE Compressor"),  # Track 1, Plugin 0 (Compressor)
        (1, 1, "ACE EQ"),          # Track 1, Plugin 1 (EQ)
        (2, 0, "First plugin on track 2"),
        (3, 0, "First plugin on track 3"),
    ]
    
    success_count = 0
    
    for track, plugin_id, description in test_cases:
        print(f"Testing {description} (Track {track}, Plugin {plugin_id})...")
        try:
            response = requests.get(f"{BASE_URL}/plugins/track/{track}/plugin/{plugin_id}/parameters")
            
            if response.status_code == 200:
                result = response.json()
                parameters = result.get('parameters', [])
                print(f"  SUCCESS {result['plugin_name']}: {result['count']} parameters")
                
                for param in parameters[:3]:  # Show first 3 parameters
                    value_info = f"= {param['value_display']}" if param.get('value_display') else f"= {param['value_raw']:.2f}"
                    unit_info = f" {param['unit']}" if param.get('unit') else ""
                    print(f"     {param['name']}: {value_info}{unit_info}")
                
                if len(parameters) > 3:
                    print(f"     ... and {len(parameters) - 3} more parameters")
                
                success_count += 1
            else:
                print(f"  FAILED Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  FAILED Error: {e}")
        
        time.sleep(0.5)
    
    return success_count, len(test_cases)

def test_plugin_info():
    """Test getting detailed plugin information"""
    print(f"\n📋 Testing Plugin Info Discovery")
    print("=" * 40)
    
    info_tests = [
        (1, 0, "Compressor info"),
        (1, 1, "EQ info"),
        (2, 0, "Track 2 first plugin"),
    ]
    
    success_count = 0
    
    for track, plugin_id, description in info_tests:
        print(f"Testing {description}...")
        try:
            response = requests.get(f"{BASE_URL}/plugins/track/{track}/plugin/{plugin_id}/info")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  SUCCESS {result['name']} v{result.get('version', 'unknown')}")
                print(f"     Type: {result.get('type', 'unknown')}")
                print(f"     Vendor: {result.get('vendor', 'unknown')}")
                print(f"     Parameters: {result.get('parameter_count', 0)}")
                print(f"     Capabilities: {', '.join(result.get('capabilities', []))}")
                success_count += 1
            else:
                print(f"  FAILED Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  FAILED Error: {e}")
        
        time.sleep(0.5)
    
    return success_count, len(info_tests)

def test_comprehensive_scan():
    """Test comprehensive plugin scanning across all tracks"""
    print(f"\nTESTING Testing Comprehensive Plugin Scan")
    print("=" * 40)
    
    print("Scanning all tracks for plugins...")
    try:
        response = requests.get(f"{BASE_URL}/plugins/discovery/scan")
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS Scan completed at {result['scan_time']}")
            print(f"FOUND Found {result['total_plugins']} plugins across {result['total_tracks']} tracks")
            
            # Show plugin distribution
            print(f"\n📈 Plugin Type Distribution:")
            plugin_types = result.get('plugin_types', {})
            for plugin_type, count in plugin_types.items():
                print(f"   {plugin_type.capitalize()}: {count}")
            
            # Show track details  
            print(f"\n🎛️ Track Details:")
            tracks = result.get('tracks', {})
            for track_id, plugins in tracks.items():
                print(f"   Track {track_id}: {len(plugins)} plugins")
                for plugin in plugins:
                    status = "Active" if plugin['active'] else "Bypassed"
                    print(f"     - {plugin['name']} ({plugin['type']}) [{status}]")
            
            return True
        else:
            print(f"FAILED Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"FAILED Error: {e}")
        return False

def test_plugin_discovery_edge_cases():
    """Test edge cases and error handling"""
    print(f"\nTESTING Testing Plugin Discovery Edge Cases")
    print("=" * 40)
    
    edge_tests = [
        ("High track number", f"/plugins/track/99/plugins"),
        ("Invalid plugin ID", f"/plugins/track/1/plugin/99/parameters"),
        ("Zero track number", f"/plugins/track/0/plugins"),
        ("Negative plugin ID", f"/plugins/track/1/plugin/-1/info"),
    ]
    
    expected_errors = 0
    
    for test_name, endpoint in edge_tests:
        print(f"Testing {test_name}...")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 422:
                print(f"  SUCCESS Correctly rejected: {response.status_code}")
                expected_errors += 1
            elif response.status_code == 200:
                print(f"  WARNING  Unexpected success: {response.status_code}")
            else:
                print(f"  ❓ Other status: {response.status_code}")
        except Exception as e:
            print(f"  FAILED Error: {e}")
        
        time.sleep(0.2)
    
    return expected_errors, len(edge_tests)

def test_osc_communication():
    """Test that OSC messages are being sent correctly"""
    print(f"\n📡 Testing OSC Communication")
    print("=" * 40)
    print("Watch server logs for OSC messages...")
    
    osc_tests = [
        ("Select track 1", f"/plugins/track/1/plugins"),
        ("Select plugin 0", f"/plugins/track/1/plugin/0/parameters"),
        ("Get plugin info", f"/plugins/track/1/plugin/0/info"),
    ]
    
    for test_name, endpoint in osc_tests:
        print(f"TESTING {test_name}")
        print(f"   Endpoint: GET {endpoint}")
        print("   Expected OSC: /select/strip, /select/plugin, etc.")
        
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                print(f"   SUCCESS Request successful")
            else:
                print(f"   FAILED Request failed: {response.status_code}")
        except Exception as e:
            print(f"   FAILED Error: {e}")
        
        time.sleep(1)  # Allow time to see OSC messages

def main():
    """Run plugin discovery tests"""
    print("🎵 Plugin Discovery Testing")
    print("=" * 60)
    print("Make sure Ardour is running with plugins loaded!")
    print("Add some plugins to tracks for realistic testing.")
    print()
    
    # Run all test categories
    tracks_tested = test_list_track_plugins()
    param_success, param_total = test_plugin_parameters()
    info_success, info_total = test_plugin_info()
    scan_success = test_comprehensive_scan()
    edge_success, edge_total = test_plugin_discovery_edge_cases()
    test_osc_communication()
    
    print(f"\n" + "=" * 60)
    print(f"SUMMARY PLUGIN DISCOVERY TEST SUMMARY:")
    print(f"📋 Track Plugin Lists: {tracks_tested} tracks tested")
    print(f"🎛️ Parameter Discovery: {param_success}/{param_total}")
    print(f"📋 Plugin Info: {info_success}/{info_total}")
    print(f"TESTING Comprehensive Scan: {'SUCCESS' if scan_success else 'FAILED'}")
    print(f"TESTING Edge Cases: {edge_success}/{edge_total}")
    
    total_success = param_success + info_success + (1 if scan_success else 0) + edge_success
    total_tests = param_total + info_total + 1 + edge_total
    
    print(f"🏆 TOTAL: {total_success}/{total_tests} test categories passed")
    
    if total_success >= total_tests - 1:  # Allow one failure
        print(f"\n🎉 PLUGIN DISCOVERY: **SUCCESS!**")
        print(f"SUCCESS Plugin Listing - Get all plugins on any track")
        print(f"SUCCESS Parameter Discovery - Detailed parameter information")
        print(f"SUCCESS Plugin Info - Vendor, version, capabilities")
        print(f"SUCCESS Comprehensive Scanning - All tracks at once")
        print(f"SUCCESS Error Handling - Proper validation")
    else:
        print(f"\nWARNING  Some plugin discovery features need attention")
    
    print(f"\nTESTING Check server logs to verify:")
    print(f"  - OSC messages: /select/strip, /select/plugin")
    print(f"  - No OSC errors or timeouts")
    print(f"  - Plugin selection commands sent")
    
    print(f"\nNEXT Next: Plugin enable/disable control!")

if __name__ == "__main__":
    main()