#!/usr/bin/env python3
"""
Full Plugin Workflow Test - End-to-End Testing with Real Ardour Session
"""

import requests
import json
import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🎵 {title}")
    print(f"{'='*60}")

def print_step(step_num, title):
    """Print a formatted step header"""
    print(f"\n📋 STEP {step_num}: {title}")
    print(f"{'-'*50}")

def test_connection():
    """Test basic server connection"""
    print_step(1, "Testing Server Connection")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running and healthy")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure to run: python -m mcp_server.main")
        return False

def test_ardour_connection():
    """Test OSC connection to Ardour"""
    print_step(2, "Testing Ardour OSC Connection")
    
    print("🔍 Testing transport control (should make Ardour respond)...")
    
    try:
        # Test play command
        response = requests.post(f"{BASE_URL}/transport/play")
        if response.status_code == 200:
            print("✅ Transport play command sent successfully")
        else:
            print(f"❌ Transport play failed: {response.status_code}")
            
        time.sleep(1)
        
        # Test stop command
        response = requests.post(f"{BASE_URL}/transport/stop")
        if response.status_code == 200:
            print("✅ Transport stop command sent successfully")
        else:
            print(f"❌ Transport stop failed: {response.status_code}")
            
        print("👁️  MANUAL CHECK: Did Ardour's playhead move? If yes, OSC connection works!")
        return True
        
    except Exception as e:
        print(f"❌ OSC connection test failed: {e}")
        return False

def setup_test_session():
    """Guide user through setting up a test session"""
    print_step(3, "Setting Up Test Session in Ardour")
    
    print("🎛️  MANUAL SETUP REQUIRED:")
    print("1. Start Ardour and create/open a session")
    print("2. Enable OSC: Edit → Preferences → Control Surfaces → OSC")
    print("3. Set OSC port to 3819 (default)")
    print("4. Add some tracks (at least 3 tracks)")
    print("5. Add plugins to tracks:")
    print("   - Track 1: Add a Compressor plugin")
    print("   - Track 2: Add an EQ plugin") 
    print("   - Track 3: Add any other plugin (reverb, delay, etc.)")
    print("6. Make sure plugins are enabled (not bypassed)")
    print()
    
    input("Press Enter when Ardour is set up with plugins loaded...")
    return True

def discover_plugins():
    """Discover plugins on tracks"""
    print_step(4, "Discovering Plugins on Tracks")
    
    discovered_plugins = {}
    
    for track_num in range(1, 4):  # Test tracks 1-3
        print(f"\n🔍 Discovering plugins on Track {track_num}...")
        
        try:
            response = requests.get(f"{BASE_URL}/plugins/track/{track_num}/plugins")
            
            if response.status_code == 200:
                result = response.json()
                plugins = result.get('plugins', [])
                discovered_plugins[track_num] = plugins
                
                if plugins:
                    print(f"✅ Found {len(plugins)} plugin(s)")
                    for plugin in plugins:
                        status = "🟢 Active" if plugin['active'] else "🔴 Bypassed"
                        print(f"   Plugin {plugin['id']}: {plugin['name']} ({plugin.get('type', 'unknown')}) {status}")
                else:
                    print("⚠️  No plugins found - make sure plugins are loaded in Ardour")
                    
            else:
                print(f"❌ Failed to discover plugins: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error discovering plugins: {e}")
            
        time.sleep(1)
    
    return discovered_plugins

def test_plugin_parameters(discovered_plugins):
    """Test plugin parameter discovery"""
    print_step(5, "Testing Plugin Parameter Discovery")
    
    parameter_data = {}
    
    for track_num, plugins in discovered_plugins.items():
        if not plugins:
            continue
            
        print(f"\n🎛️  Testing parameters for Track {track_num} plugins...")
        
        for plugin in plugins:
            plugin_id = plugin['id']
            plugin_name = plugin['name']
            
            print(f"\n🔍 Getting parameters for {plugin_name} (ID: {plugin_id})...")
            
            try:
                response = requests.get(f"{BASE_URL}/plugins/track/{track_num}/plugin/{plugin_id}/parameters")
                
                if response.status_code == 200:
                    result = response.json()
                    parameters = result.get('parameters', [])
                    parameter_data[f"{track_num}_{plugin_id}"] = parameters
                    
                    if parameters:
                        print(f"✅ Found {len(parameters)} parameter(s)")
                        for param in parameters[:5]:  # Show first 5
                            value_display = param.get('value_display', f"{param['value_raw']:.2f}")
                            print(f"   {param['name']}: {value_display}")
                        
                        if len(parameters) > 5:
                            print(f"   ... and {len(parameters) - 5} more parameters")
                    else:
                        print("⚠️  No parameters found")
                        
                else:
                    print(f"❌ Failed to get parameters: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error getting parameters: {e}")
                
            time.sleep(1)
    
    return parameter_data

def test_plugin_control(discovered_plugins):
    """Test plugin control operations"""
    print_step(6, "Testing Plugin Control Operations")
    
    for track_num, plugins in discovered_plugins.items():
        if not plugins:
            continue
            
        plugin = plugins[0]  # Test first plugin on each track
        plugin_id = plugin['id']
        plugin_name = plugin['name']
        
        print(f"\n🎛️  Testing control for {plugin_name} on Track {track_num}...")
        
        # Test 1: Plugin bypass/enable
        print("🔄 Testing plugin bypass/enable...")
        
        try:
            # Bypass plugin
            response = requests.post(f"{BASE_URL}/plugins/track/{track_num}/plugin/{plugin_id}/bypass")
            if response.status_code == 200:
                print("✅ Plugin bypass successful")
            else:
                print(f"❌ Plugin bypass failed: {response.status_code}")
                
            time.sleep(1)
            
            # Enable plugin
            response = requests.post(f"{BASE_URL}/plugins/track/{track_num}/plugin/{plugin_id}/enable")
            if response.status_code == 200:
                print("✅ Plugin enable successful")
            else:
                print(f"❌ Plugin enable failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Plugin control error: {e}")
            
        # Test 2: Smart parameter control
        print("🎚️  Testing smart parameter control...")
        
        try:
            # Test different parameter types based on plugin type
            if 'comp' in plugin_name.lower():
                # Test compressor threshold
                response = requests.post(
                    f"{BASE_URL}/plugins/track/{track_num}/plugin/{plugin_id}/parameter/threshold",
                    json={"db": -18.0}
                )
                if response.status_code == 200:
                    print("✅ Compressor threshold control successful")
                else:
                    print(f"❌ Compressor threshold control failed: {response.status_code}")
                    
            elif 'eq' in plugin_name.lower():
                # Test EQ frequency
                response = requests.post(
                    f"{BASE_URL}/plugins/track/{track_num}/plugin/{plugin_id}/parameter/frequency",
                    json={"hz": 1000.0}
                )
                if response.status_code == 200:
                    print("✅ EQ frequency control successful")
                else:
                    print(f"❌ EQ frequency control failed: {response.status_code}")
                    
            else:
                # Test generic parameter control
                response = requests.post(
                    f"{BASE_URL}/plugins/track/{track_num}/plugin/{plugin_id}/parameter/gain",
                    json={"db": 0.0}
                )
                if response.status_code == 200:
                    print("✅ Generic parameter control successful")
                else:
                    print(f"❌ Generic parameter control failed: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Parameter control error: {e}")
            
        time.sleep(1)

def test_comprehensive_scan():
    """Test comprehensive plugin scanning"""
    print_step(7, "Testing Comprehensive Plugin Scanning")
    
    print("🔍 Running comprehensive plugin scan...")
    
    try:
        response = requests.get(f"{BASE_URL}/plugins/discovery/scan")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Scan completed at {result['scan_time']}")
            print(f"📊 Found {result['total_plugins']} plugins across {result['total_tracks']} tracks")
            
            # Show plugin distribution
            plugin_types = result.get('plugin_types', {})
            if plugin_types:
                print(f"\n📈 Plugin Type Distribution:")
                for plugin_type, count in plugin_types.items():
                    print(f"   {plugin_type.capitalize()}: {count}")
            
            # Show track details
            tracks = result.get('tracks', {})
            if tracks:
                print(f"\n🎛️  Track Details:")
                for track_id, plugins in tracks.items():
                    if plugins:
                        print(f"   Track {track_id}: {len(plugins)} plugins")
                        for plugin in plugins:
                            status = "Active" if plugin['active'] else "Bypassed"
                            print(f"     - {plugin['name']} ({plugin['type']}) [{status}]")
                            
            return result
            
        else:
            print(f"❌ Scan failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Scan error: {e}")
        return None

def validate_results(discovered_plugins, parameter_data, scan_result):
    """Validate and summarize test results"""
    print_step(8, "Validating Results")
    
    print("🔍 Validation Summary:")
    
    # Count totals
    total_plugins = sum(len(plugins) for plugins in discovered_plugins.values())
    total_parameters = sum(len(params) for params in parameter_data.values())
    
    print(f"📊 Total plugins discovered: {total_plugins}")
    print(f"📊 Total parameters discovered: {total_parameters}")
    
    # Validate plugin types
    plugin_types = set()
    for plugins in discovered_plugins.values():
        for plugin in plugins:
            plugin_types.add(plugin.get('type', 'unknown'))
    
    print(f"📊 Plugin types found: {', '.join(plugin_types)}")
    
    # Check for real vs. hardcoded data
    real_data_indicators = 0
    hardcoded_indicators = 0
    
    for plugins in discovered_plugins.values():
        for plugin in plugins:
            if plugin['name'] in ['ACE Compressor', 'ACE EQ', 'ACE Limiter']:
                hardcoded_indicators += 1
            else:
                real_data_indicators += 1
    
    print(f"📊 Real plugin data: {real_data_indicators}")
    print(f"📊 Hardcoded indicators: {hardcoded_indicators}")
    
    # Overall assessment
    success_score = 0
    if total_plugins > 0:
        success_score += 30
    if total_parameters > 0:
        success_score += 30
    if real_data_indicators > hardcoded_indicators:
        success_score += 40
    
    print(f"\n🎯 Overall Success Score: {success_score}/100")
    
    if success_score >= 80:
        print("🎉 EXCELLENT: Real plugin discovery is working!")
    elif success_score >= 60:
        print("✅ GOOD: Plugin discovery is mostly working")
    else:
        print("⚠️  NEEDS WORK: Plugin discovery needs improvement")

def main():
    """Run full plugin workflow test"""
    print_section("FULL PLUGIN WORKFLOW TEST")
    
    print("🚀 This test will verify the complete plugin discovery and control workflow")
    print("📋 Prerequisites:")
    print("   - Ardour running with OSC enabled")
    print("   - MCP server running (python -m mcp_server.main)")
    print("   - Test session with plugins loaded")
    print()
    
    # Run all test steps
    if not test_connection():
        print("\n❌ Cannot proceed without server connection")
        return
        
    if not test_ardour_connection():
        print("\n⚠️  OSC connection may not be working")
        
    setup_test_session()
    discovered_plugins = discover_plugins()
    parameter_data = test_plugin_parameters(discovered_plugins)
    test_plugin_control(discovered_plugins)
    scan_result = test_comprehensive_scan()
    validate_results(discovered_plugins, parameter_data, scan_result)
    
    # Final summary
    print_section("FINAL SUMMARY")
    
    print("🎯 TEST COMPLETION CHECKLIST:")
    print("✅ Server connection tested")
    print("✅ Ardour OSC connection tested")
    print("✅ Plugin discovery tested")
    print("✅ Parameter discovery tested")
    print("✅ Plugin control tested")
    print("✅ Comprehensive scanning tested")
    print("✅ Results validated")
    
    print(f"\n🚀 NEXT STEPS:")
    print("1. If plugins were discovered: Real plugin discovery is working!")
    print("2. If no plugins found: Check Ardour setup and OSC configuration")
    print("3. Test with different plugin types and parameters")
    print("4. Implement additional plugin management features")
    
    print(f"\n🔧 TROUBLESHOOTING:")
    print("- No plugins found: Ensure plugins are loaded in Ardour tracks")
    print("- OSC errors: Check Ardour OSC settings (port 3819)")
    print("- Parameter errors: Some plugins may have non-standard parameter names")
    print("- Control errors: Check plugin supports OSC parameter control")

if __name__ == "__main__":
    main()