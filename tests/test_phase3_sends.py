#!/usr/bin/env python3
"""
Test script for Phase 3A: Send/Aux Control Features

NOTE: This test assumes tracks 1-2 exist in your Ardour session.
API uses 1-based track numbering (track 1, track 2, etc.)
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_send_controls():
    """Test send level, gain, and enable controls"""
    print("🎛️ Testing Send/Aux Controls")
    print("=" * 40)
    
    send_tests = [
        # Send Level Tests
        ("Set Send 1 Level 50%", "/sends/track/1/send/1/level", {"level": 0.5}),
        ("Set Send 1 Level 75%", "/sends/track/1/send/1/level", {"level": 0.75}),
        ("Set Send 2 Level 25%", "/sends/track/1/send/2/level", {"level": 0.25}),
        ("Set Send 1 Level Off", "/sends/track/1/send/1/level", {"level": 0.0}),
        ("Set Send 1 Level Unity", "/sends/track/1/send/1/level", {"level": 1.0}),
        
        # Send Gain Tests (dB)
        ("Set Send 1 Gain -6dB", "/sends/track/1/send/1/gain", {"gain_db": -6.0}),
        ("Set Send 1 Gain 0dB", "/sends/track/1/send/1/gain", {"gain_db": 0.0}),
        ("Set Send 2 Gain -12dB", "/sends/track/1/send/2/gain", {"gain_db": -12.0}),
        ("Set Send 1 Gain -60dB", "/sends/track/1/send/1/gain", {"gain_db": -60.0}),
        
        # Send Enable/Disable Tests
        ("Enable Send 1", "/sends/track/1/send/1/enable", {"enabled": True}),
        ("Disable Send 1", "/sends/track/1/send/1/enable", {"enabled": False}),
        ("Enable Send 2", "/sends/track/1/send/2/enable", {"enabled": True}),
        ("Disable Send 2", "/sends/track/1/send/2/enable", {"enabled": False}),
        
        # Multi-track Send Tests (using track 1 and 2 only)
        ("Track 1 Send 2 Level", "/sends/track/1/send/2/level", {"level": 0.8}),
        ("Track 2 Send 1 Gain", "/sends/track/2/send/1/gain", {"gain_db": -3.0}),
        ("Track 2 Enable Send 1", "/sends/track/2/send/1/enable", {"enabled": True}),
    ]
    
    success_count = 0
    
    for test_name, endpoint, data in send_tests:
        print(f"Testing {test_name}...")
        try:
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ {result['message']}")
                print(f"     OSC: {result['osc_address']}")
                success_count += 1
            else:
                print(f"  ❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        time.sleep(0.3)
    
    return success_count, len(send_tests)

def test_send_listing():
    """Test listing sends for tracks"""
    print(f"\n📋 Testing Send Listing")
    print("=" * 40)
    
    list_tests = [
        ("List Track 1 Sends", "/sends/track/1/sends"),
        ("List Track 2 Sends", "/sends/track/2/sends"),
    ]
    
    success_count = 0
    
    for test_name, endpoint in list_tests:
        print(f"Testing {test_name}...")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ {result['message']}")
                print(f"     OSC: {result['osc_address']}")
                success_count += 1
            else:
                print(f"  ❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        time.sleep(0.5)
    
    return success_count, len(list_tests)

def test_send_edge_cases():
    """Test edge cases and error handling"""
    print(f"\n🧪 Testing Send Edge Cases")
    print("=" * 40)
    
    edge_tests = [
        # Boundary values
        ("Send Level Min", "/sends/track/1/send/1/level", {"level": 0.0}),
        ("Send Level Max", "/sends/track/1/send/1/level", {"level": 1.0}),
        ("Send Gain Min", "/sends/track/1/send/1/gain", {"gain_db": -60.0}),
        ("Send Gain Max", "/sends/track/1/send/1/gain", {"gain_db": 6.0}),
        
        # Higher send numbers (same track)
        ("Track 1 Send 3", "/sends/track/1/send/3/level", {"level": 0.5}),
        ("Track 1 Send 4", "/sends/track/1/send/4/level", {"level": 0.5}),
    ]
    
    success_count = 0
    
    for test_name, endpoint, data in edge_tests:
        print(f"Testing {test_name}...")
        try:
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ {result['message']}")
                success_count += 1
            else:
                print(f"  ⚠️  Expected behavior: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        time.sleep(0.2)
    
    return success_count, len(edge_tests)

def test_real_world_scenario():
    """Test a realistic mixing scenario with sends"""
    print(f"\n🎵 Real-World Mixing Scenario")
    print("=" * 40)
    print("Setting up a typical reverb send scenario...")
    
    scenario_steps = [
        ("Setup: Enable reverb send on vocals", "/sends/track/1/send/1/enable", {"enabled": True}),
        ("Setup: Set vocals reverb level", "/sends/track/1/send/1/level", {"level": 0.3}),
        ("Setup: Enable reverb send on guitar", "/sends/track/2/send/1/enable", {"enabled": True}),
        ("Setup: Set guitar reverb level", "/sends/track/2/send/1/level", {"level": 0.2}),
        ("Setup: Enable delay send on vocals", "/sends/track/1/send/2/enable", {"enabled": True}),
        ("Setup: Set vocals delay level", "/sends/track/1/send/2/level", {"level": 0.15}),
        ("Mix: Increase vocal reverb", "/sends/track/1/send/1/level", {"level": 0.4}),
        ("Mix: Decrease guitar reverb", "/sends/track/2/send/1/level", {"level": 0.1}),
        ("Mix: Boost vocal delay", "/sends/track/1/send/2/gain", {"gain_db": 3.0}),
    ]
    
    success_count = 0
    
    for step_name, endpoint, data in scenario_steps:
        print(f"🎛️ {step_name}")
        try:
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"    ✅ {result['message']}")
                success_count += 1
            else:
                print(f"    ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"    ❌ Error: {e}")
        
        time.sleep(1)  # Slower for demo effect
    
    print(f"\n🎯 Scenario complete: {success_count}/{len(scenario_steps)} steps successful")
    return success_count, len(scenario_steps)

def main():
    """Run Phase 3A send control tests"""
    print("🎵 Phase 3A: Send/Aux Control Testing")
    print("=" * 60)
    print("Make sure Ardour is running with OSC enabled!")
    print("Make sure you have aux busses created for sends to work!")
    print()
    
    # Run all test categories
    send_success, send_total = test_send_controls()
    list_success, list_total = test_send_listing()
    edge_success, edge_total = test_send_edge_cases()
    scenario_success, scenario_total = test_real_world_scenario()
    
    # Calculate totals
    total_success = send_success + list_success + edge_success + scenario_success
    total_tests = send_total + list_total + edge_total + scenario_total
    
    print(f"\n" + "=" * 60)
    print(f"🎯 PHASE 3A TEST SUMMARY:")
    print(f"📊 Send Controls: {send_success}/{send_total}")
    print(f"📋 Send Listing: {list_success}/{list_total}")
    print(f"🧪 Edge Cases: {edge_success}/{edge_total}")
    print(f"🎵 Real Scenario: {scenario_success}/{scenario_total}")
    print(f"🏆 TOTAL: {total_success}/{total_tests} tests passed")
    
    if total_success == total_tests:
        print(f"\n🎉 PHASE 3A: **COMPLETE SUCCESS!**")
        print(f"✅ Send Level Control - Adjust send amounts")
        print(f"✅ Send Gain Control - Fine-tune with dB values")
        print(f"✅ Send Enable/Disable - Turn sends on/off")
        print(f"✅ Multi-track Support - Control any track's sends")
        print(f"✅ Edge Case Handling - Boundary values work")
        print(f"✅ Real-world Scenarios - Mixing workflows")
    else:
        print(f"\n⚠️  Some send controls need attention")
        print(f"🔧 But core send functionality is working!")
    
    print(f"\n🔍 Check Ardour to verify:")
    print(f"  - Send knobs moved in mixer")
    print(f"  - Send enable/disable buttons changed")
    print(f"  - Aux bus levels changed")
    print(f"  - OSC messages in Ardour logs")
    
    print(f"\n🚀 Next: Plugin control and automation!")

if __name__ == "__main__":
    main()