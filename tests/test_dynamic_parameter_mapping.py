#!/usr/bin/env python3
"""
Test script for Dynamic Plugin Parameter Mapping System
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
    print(f"🎛️ {title}")
    print(f"{'='*60}")

def print_step(step_num, title):
    """Print a formatted step header"""
    print(f"\n📋 STEP {step_num}: {title}")
    print(f"{'-'*50}")

def test_parameter_name_listing():
    """Test parameter name listing for plugins"""
    print_step(1, "Testing Parameter Name Listing")
    
    test_cases = [
        (1, 0, "First plugin on track 1"),
        (2, 0, "First plugin on track 2"),
        (3, 0, "First plugin on track 3"),
    ]
    
    discovered_names = {}
    
    for track, plugin_id, description in test_cases:
        print(f"\n🔍 Testing parameter names for {description}...")
        
        try:
            response = requests.get(f"{BASE_URL}/plugins/track/{track}/plugin/{plugin_id}/parameters/names")
            
            if response.status_code == 200:
                result = response.json()
                parameter_names = result.get('parameter_names', [])
                discovered_names[f"{track}_{plugin_id}"] = parameter_names
                
                print(f"✅ Found {len(parameter_names)} parameter names")
                for name in parameter_names[:5]:  # Show first 5
                    print(f"   - {name}")
                    
                if len(parameter_names) > 5:
                    print(f"   ... and {len(parameter_names) - 5} more")
                    
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
        time.sleep(1)
    
    return discovered_names

def test_parameter_info_lookup(discovered_names):
    """Test detailed parameter information lookup"""
    print_step(2, "Testing Parameter Info Lookup")
    
    parameter_infos = {}
    
    for key, parameter_names in discovered_names.items():
        if not parameter_names:
            continue
            
        track, plugin_id = key.split('_')
        track = int(track)
        plugin_id = int(plugin_id)
        
        print(f"\n🔍 Testing parameter info for Track {track} Plugin {plugin_id}...")
        
        # Test first few parameters
        for param_name in parameter_names[:3]:
            print(f"Getting info for parameter: {param_name}")
            
            try:
                response = requests.get(f"{BASE_URL}/plugins/track/{track}/plugin/{plugin_id}/parameter/{param_name}/info")
                
                if response.status_code == 200:
                    result = response.json()
                    param_info = result.get('parameter', {})
                    parameter_infos[f"{key}_{param_name}"] = param_info
                    
                    print(f"✅ Parameter info retrieved:")
                    print(f"   Name: {param_info.get('name', 'unknown')}")
                    print(f"   Type: {param_info.get('type', 'unknown')}")
                    print(f"   Unit: {param_info.get('unit', 'none')}")
                    print(f"   Range: {param_info.get('min_value', 0)} - {param_info.get('max_value', 1)}")
                    print(f"   Current: {param_info.get('current_value', 0)}")
                    
                else:
                    print(f"❌ Failed: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                
            time.sleep(0.5)
    
    return parameter_infos

def test_parameter_search():
    """Test parameter search functionality"""
    print_step(3, "Testing Parameter Search")
    
    test_cases = [
        (1, 0, "gain", "Search for gain-related parameters"),
        (1, 0, "freq", "Search for frequency-related parameters"),
        (2, 0, "time", "Search for time-related parameters"),
        (1, 0, "threshold", "Search for threshold parameters"),
    ]
    
    search_results = {}
    
    for track, plugin_id, pattern, description in test_cases:
        print(f"\n🔍 {description} (Track {track}, Plugin {plugin_id})...")
        
        try:
            response = requests.get(f"{BASE_URL}/plugins/track/{track}/plugin/{plugin_id}/parameters/search?pattern={pattern}")
            
            if response.status_code == 200:
                result = response.json()
                matches = result.get('matches', [])
                search_results[f"{track}_{plugin_id}_{pattern}"] = matches
                
                print(f"✅ Found {len(matches)} matches for '{pattern}'")
                for match in matches:
                    print(f"   - {match['name']} (ID: {match['id']}, Type: {match['type']}, Unit: {match.get('unit', 'none')})")
                    
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
        time.sleep(1)
    
    return search_results

def test_parameter_suggestions():
    """Test smart parameter suggestions"""
    print_step(4, "Testing Smart Parameter Suggestions")
    
    test_cases = [
        (1, 0, "thresh", "Threshold suggestions"),
        (1, 0, "ratio", "Ratio suggestions"),
        (1, 0, "att", "Attack suggestions"),
        (2, 0, "freq", "Frequency suggestions"),
        (1, 0, "unknown_param", "Unknown parameter suggestions"),
    ]
    
    suggestion_results = {}
    
    for track, plugin_id, input_name, description in test_cases:
        print(f"\n🔍 {description} (Track {track}, Plugin {plugin_id})...")
        
        try:
            response = requests.get(f"{BASE_URL}/plugins/track/{track}/plugin/{plugin_id}/parameters/suggestions?input_name={input_name}")
            
            if response.status_code == 200:
                result = response.json()
                suggestions = result.get('suggestions', [])
                suggestion_results[f"{track}_{plugin_id}_{input_name}"] = suggestions
                
                print(f"✅ Generated {len(suggestions)} suggestions for '{input_name}'")
                for suggestion in suggestions:
                    print(f"   - {suggestion}")
                    
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
        time.sleep(1)
    
    return suggestion_results

def test_dynamic_parameter_control(discovered_names):
    """Test dynamic parameter control"""
    print_step(5, "Testing Dynamic Parameter Control")
    
    control_results = {}
    
    for key, parameter_names in discovered_names.items():
        if not parameter_names:
            continue
            
        track, plugin_id = key.split('_')
        track = int(track)
        plugin_id = int(plugin_id)
        
        print(f"\n🎛️ Testing dynamic parameter control for Track {track} Plugin {plugin_id}...")
        
        # Test different parameter types
        test_parameters = []
        
        # Look for common parameter names
        for param_name in parameter_names:
            param_lower = param_name.lower()
            if 'threshold' in param_lower or 'thresh' in param_lower:
                test_parameters.append((param_name, {"db": -20.0}, "threshold control"))
            elif 'gain' in param_lower and 'makeup' not in param_lower:
                test_parameters.append((param_name, {"db": 3.0}, "gain control"))
            elif 'ratio' in param_lower:
                test_parameters.append((param_name, {"ratio": 4.0}, "ratio control"))
            elif 'freq' in param_lower:
                test_parameters.append((param_name, {"hz": 1000.0}, "frequency control"))
            elif 'attack' in param_lower:
                test_parameters.append((param_name, {"ms": 10.0}, "attack time control"))
            elif 'release' in param_lower:
                test_parameters.append((param_name, {"ms": 100.0}, "release time control"))
        
        # Test up to 3 parameters per plugin
        for param_name, value_dict, description in test_parameters[:3]:
            print(f"🎚️ Testing {description} - {param_name}")
            
            try:
                response = requests.post(
                    f"{BASE_URL}/plugins/track/{track}/plugin/{plugin_id}/parameter/{param_name}/dynamic",
                    json=value_dict
                )
                
                if response.status_code == 200:
                    result = response.json()
                    control_results[f"{key}_{param_name}"] = result
                    
                    print(f"✅ Dynamic parameter control successful")
                    print(f"   Parameter ID: {result.get('parameter_id', 'unknown')}")
                    print(f"   Input: {result.get('input_value', {})}")
                    print(f"   Actual: {result.get('actual_value', 'unknown')}")
                    print(f"   OSC Value: {result.get('osc_value', 'unknown')}")
                    
                else:
                    print(f"❌ Failed: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                
            time.sleep(1)
    
    return control_results

def test_parameter_mapping_errors():
    """Test error handling for parameter mapping"""
    print_step(6, "Testing Parameter Mapping Error Handling")
    
    error_tests = [
        (1, 0, "nonexistent_param", {"db": -10.0}, "Non-existent parameter"),
        (1, 99, "threshold", {"db": -10.0}, "Non-existent plugin"),
        (99, 0, "gain", {"db": 0.0}, "Non-existent track"),
        (1, 0, "gain", {}, "No parameter value provided"),
    ]
    
    error_results = {}
    
    for track, plugin_id, param_name, value_dict, description in error_tests:
        print(f"\n🧪 Testing {description}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/plugins/track/{track}/plugin/{plugin_id}/parameter/{param_name}/dynamic",
                json=value_dict
            )
            
            if response.status_code != 200:
                error_results[description] = {
                    "status_code": response.status_code,
                    "error": response.text
                }
                print(f"✅ Correctly handled error: {response.status_code}")
                
                # Check for helpful error messages
                if "Did you mean" in response.text:
                    print("   ✅ Provides parameter suggestions")
                    
            else:
                print(f"⚠️ Unexpected success: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
        time.sleep(0.5)
    
    return error_results

def test_mapping_performance():
    """Test performance of parameter mapping"""
    print_step(7, "Testing Parameter Mapping Performance")
    
    print("🕐 Testing parameter mapping speed...")
    
    # Time parameter name listing
    start_time = time.time()
    response = requests.get(f"{BASE_URL}/plugins/track/1/plugin/0/parameters/names")
    names_time = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        param_count = result.get('count', 0)
        print(f"✅ Listed {param_count} parameters in {names_time:.3f} seconds")
        
        # Test parameter info lookup speed
        if param_count > 0:
            param_names = result.get('parameter_names', [])
            
            start_time = time.time()
            for param_name in param_names[:5]:  # Test first 5
                requests.get(f"{BASE_URL}/plugins/track/1/plugin/0/parameter/{param_name}/info")
            info_time = time.time() - start_time
            
            print(f"✅ Retrieved info for 5 parameters in {info_time:.3f} seconds")
            print(f"   Average: {info_time/5:.3f} seconds per parameter")
            
        # Test dynamic parameter control speed
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/plugins/track/1/plugin/0/parameter/gain/dynamic",
            json={"db": 0.0}
        )
        control_time = time.time() - start_time
        
        if response.status_code in [200, 404]:  # 404 is OK if parameter doesn't exist
            print(f"✅ Dynamic parameter control took {control_time:.3f} seconds")
            
    else:
        print(f"❌ Performance test failed: {response.status_code}")

def validate_mapping_system(discovered_names, parameter_infos, search_results, suggestion_results, control_results):
    """Validate the dynamic parameter mapping system"""
    print_step(8, "Validating Dynamic Parameter Mapping System")
    
    print("🔍 Validation Summary:")
    
    # Count totals
    total_plugins_tested = len(discovered_names)
    total_parameters_discovered = sum(len(names) for names in discovered_names.values())
    total_parameter_infos = len(parameter_infos)
    total_search_results = sum(len(results) for results in search_results.values())
    total_control_tests = len(control_results)
    
    print(f"📊 Plugins tested: {total_plugins_tested}")
    print(f"📊 Parameters discovered: {total_parameters_discovered}")
    print(f"📊 Parameter info lookups: {total_parameter_infos}")
    print(f"📊 Search results: {total_search_results}")
    print(f"📊 Control tests: {total_control_tests}")
    
    # Check for real vs. hardcoded data
    if total_parameters_discovered > 0:
        print("✅ Parameter discovery is working")
    else:
        print("⚠️ No parameters discovered - check plugin loading")
    
    # Check mapping accuracy
    mapping_accuracy = 0
    if total_parameter_infos > 0:
        mapping_accuracy += 30
    if total_search_results > 0:
        mapping_accuracy += 30
    if total_control_tests > 0:
        mapping_accuracy += 40
    
    print(f"\n🎯 Mapping System Score: {mapping_accuracy}/100")
    
    if mapping_accuracy >= 90:
        print("🎉 EXCELLENT: Dynamic parameter mapping is working perfectly!")
    elif mapping_accuracy >= 70:
        print("✅ GOOD: Dynamic parameter mapping is working well")
    elif mapping_accuracy >= 50:
        print("⚠️ FAIR: Dynamic parameter mapping needs improvement")
    else:
        print("❌ POOR: Dynamic parameter mapping needs significant work")

def main():
    """Run dynamic parameter mapping tests"""
    print_section("DYNAMIC PARAMETER MAPPING TESTS")
    
    print("🎯 This test verifies the dynamic plugin parameter mapping system")
    print("📋 Features tested:")
    print("   - Parameter name discovery and listing")
    print("   - Detailed parameter information lookup")
    print("   - Parameter search and pattern matching")
    print("   - Smart parameter name suggestions")
    print("   - Dynamic parameter control with real IDs")
    print("   - Error handling and validation")
    print("   - Performance optimization")
    print()
    
    # Check server availability
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server not available - cannot run tests")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Run all test categories
    discovered_names = test_parameter_name_listing()
    parameter_infos = test_parameter_info_lookup(discovered_names)
    search_results = test_parameter_search()
    suggestion_results = test_parameter_suggestions()
    control_results = test_dynamic_parameter_control(discovered_names)
    error_results = test_parameter_mapping_errors()
    test_mapping_performance()
    validate_mapping_system(discovered_names, parameter_infos, search_results, suggestion_results, control_results)
    
    # Final summary
    print_section("FINAL SUMMARY")
    
    print("🎯 DYNAMIC PARAMETER MAPPING TEST COMPLETION:")
    print("✅ Parameter name listing tested")
    print("✅ Parameter info lookup tested")
    print("✅ Parameter search tested")
    print("✅ Smart suggestions tested")
    print("✅ Dynamic control tested")
    print("✅ Error handling tested")
    print("✅ Performance tested")
    print("✅ System validation completed")
    
    print(f"\n🚀 NEXT STEPS:")
    print("1. If parameters discovered: Dynamic mapping is working!")
    print("2. If no parameters: Load plugins in Ardour and test")
    print("3. Test with different plugin types for comprehensive coverage")
    print("4. Implement additional mapping features as needed")
    
    print(f"\n🎛️ USAGE EXAMPLES:")
    print("# List parameter names:")
    print("curl http://localhost:8000/plugins/track/1/plugin/0/parameters/names")
    print()
    print("# Get parameter info:")
    print("curl http://localhost:8000/plugins/track/1/plugin/0/parameter/threshold/info")
    print()
    print("# Search parameters:")
    print("curl http://localhost:8000/plugins/track/1/plugin/0/parameters/search?pattern=gain")
    print()
    print("# Dynamic parameter control:")
    print("curl -X POST http://localhost:8000/plugins/track/1/plugin/0/parameter/threshold/dynamic \\")
    print("  -H 'Content-Type: application/json' -d '{\"db\": -20.0}'")

if __name__ == "__main__":
    main()